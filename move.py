# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView
from trytond.pyson import Eval
from trytond.pool import PoolMeta, Pool
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.transaction import Transaction


__all__ = ['Move']


class Move(metaclass=PoolMeta):
    __name__ = 'account.move'

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        if 'state' not in cls._check_modify_exclude:
            cls._check_modify_exclude.append('state')
        cls._buttons.update({
            'draft': {
                'invisible': Eval('state') == 'draft',
                },
            })

    @classmethod
    @ModelView.button
    def draft(cls, moves):
        Line = Pool().get('account.move.line')
        cls.write(moves, {
            'state': 'draft',
            })
        Line.check_modify([l for m in moves for l in m.lines])

    @classmethod
    def delete(cls, moves):
        if not Transaction().context.get('draft_invoices', False):
            invoices = [move for move in moves if move.origin
                and not isinstance(move.origin, str)
                and move.origin.__name__ == 'account.invoice'
                and move.origin.state != 'draft']

            if invoices:
                names = ', '.join(m.rec_name for m in invoices[:5])
                if len(invoices) > 5:
                    names += '...'
                raise UserError(gettext('account_move_draft.msg_delete_moves_invoice',
                    moves=names))
        super(Move, cls).delete(moves)
