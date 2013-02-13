# -*- coding: utf-8 -*-
##########################################################################
# Aquasys G.K.

# Copyright (C) 20012-2013.

#

# This program is free software: you can redistribute it and/or modify

# it under the terms of the GNU Affero General Public License as

# published by the Free Software Foundation, either version 3 of the

# License, or (at your option) any later version.

#

# This program is distributed in the hope that it will be useful,

# but WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the

# GNU Affero General Public License for more details.

#

# You should have received a copy of the GNU Affero General Public License

# along with this program. If not, see <http://www.gnu.org/licenses/>.
#########################################################################
from psycopg2 import Binary
from openerp.osv import fields
import openerp.tools as tools
from openerp import SUPERUSER_ID
from . import FILE_PATH
import os

_column = fields._column


class binary(_column):
    _type = 'binary'
    _symbol_c = '%s'

    # Binary values may be byte strings (python 2.6 byte array), but
    # the legacy OpenERP convention is to transfer and store binaries
    # as base64-encoded strings. The base64 string may be provided as a
    # unicode in some circumstances, hence the str() cast in symbol_f.
    # This str coercion will only work for pure ASCII unicode strings,
    # on purpose - non base64 data must be passed as a 8bit byte strings.
    _symbol_f = lambda symb: symb and Binary(str(symb)) or None

    _symbol_set = (_symbol_c, _symbol_f)
    _symbol_get = lambda self, x: x and str(x)

    _classic_read = False
    _prefetch = False

    def __init__(self, string='unknown', filters=None, store='s3', **args):
        _column.__init__(self, string=string, **args)
        self.filters = filters
        self.store = store
        if store == 's3':
            print "0000000000000000000000000000000000000000000000000000)"
            self._classic_write = False
            self._symbol_set = (self._symbol_c, self.set)
            self._symbol_get = None

    def set(self, cr, obj, id, name, value, user=None, context=None):
        print "4444444444444444444444444444444444444444444444444444444444444"
        if self.store != 's3':
            cr.execute('update ' + obj._table + ' set'
                       + name + '=' + self._symbol_set[0] + ' where id=%s',
                       (self._symbol_set[1](value), id))
        else:
            if not user:
                user = SUPERUSER_ID
            cr.execute('select company_id from res_users where id = %s' %
                       (user))
            company_id = cr.fetchall()
            company_id = tools.misc.flatten(company_id)
            cr.execute(
                'select name from res_company where id = %s' % (company_id[0]))
            company_name = tools.misc.flatten(cr.fetchall())[0]
            path = "/home/erp/temp" or os.getenv("HOME")
            path = os.path.join(path, cr.dbname, company_name,
                                obj._name.replace(".", "_"), name)
            if not os.path.exists(path):
                os.makedirs(path)
            file_name = os.path.join(path, str(id))
            f = open(file_name, "w")
            import base64
            f.write(base64.decodestring(value))
            f.close()

    def get(self, cr, obj, ids, name, user=None, context=None, values=None):
        print "777777777777777777777777777777777777777777777777777777&&"
        if not context:
            context = {}
        if not values:
            values = []
        res = {}
        for i in ids:
            val = None
            if self.store != 's3':
                for v in values:
                    if v['id'] == i:
                        val = v[name]
                        break
            else:
                cr.execute('select company_id from res_users where id = %s' %
                           (user))
                company_id = cr.fetchall()
                company_id = tools.misc.flatten(company_id)
                cr.execute('select name from res_company where id = %s' %
                           (company_id[0]))
                company_name = tools.misc.flatten(cr.fetchall())[0]
                path = "/home/erp/temp" or os.getenv("HOME")
                file_name = os.path.join(path,
                                         cr.dbname,
                                         company_name,
                                         obj._name.replace(".", "_"),
                                         name, str(i))
                if not os.path.exists(file_name):
                    val = None
                    continue
                print "oooooooooooooO",context
                if context.get('bin_size_%s' % name, context.get('bin_size')):
                    val = os.path.getsize(file_name)
                    res[i] = val
                    continue
                else:
                    f = open(file_name, 'r')
                    data = f.read()
                    import base64
                    val = base64.encodestring(data)
                    res[i] = val
                    continue
            #       having an implicit convention for the value
            if val and context.get('bin_size_%s' % name,
                                   context.get('bin_size')):
                res[i] = tools.human_size(long(val))
            else:
                res[i] = val
        print "44444444",res
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
