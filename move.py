# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView
from trytond.pyson import Eval
from trytond.pool import PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Move']


class Move(metaclass=PoolMeta):
    __name__ = 'account.move'

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        if not 'state' in cls._check_modify_exclude:
            cls._check_modify_exclude.append('state')
        cls._buttons.update({
            'draft': {
                'invisible': Eval('state') == 'draft',
                },
            })

    @classmethod
    @ModelView.button
    def draft(cls, moves):
        cls.write(moves, {
            'state': 'draft',
            })

    @classmethod
    def delete(cls, moves):
        invoices = [move for move in moves if move.origin
            and move.origin.__name__ == 'account.invoice'
            and move.origin.state != 'draft']

        if invoices:
            names = ', '.join(m.rec_name for m in invoices[:5])
            if len(invoices) > 5:
                names += '...'
            raise UserError(gettext('account_move_draft.msg_delete_moves_invoice',
                moves=names))
        super(Move, cls).delete(moves)
