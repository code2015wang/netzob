#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByKeyField import ClusterByKeyField
from netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByApplicativeData import ClusterByApplicativeData


class FormatIdentifier(object):
    """This class is a wrapper for all the various tools
    which allow to infer the different message formats contained in one or multiple symbols.

    """

    @staticmethod
    @typeCheck(Symbol)
    def clusterByApplicativeData(symbol):
        """Regroup messages in the specified symbol having the
        same applicative data in their content.

        :param symbol: the symbol from which messages will be clustered.
        :type symbol: :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :return: a list of symbol representing all the computed clusters
        :rtype: a list of :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :raises: a TypeError if symbol is not valid.
        """
        if (symbol is None):
            raise TypeError("Symbol cannot be None")

        cluster = ClusterByApplicativeData()
        return cluster.cluster(symbol)

    @staticmethod
    @typeCheck(AbstractField, AbstractField)
    def clusterByKeyField(field, keyField):
        """Create and return new symbols according to a specific key
        field.
        This method is a wrapper for :class:`netzob.Inference.Vocabulary.FormatIdentifierOperations.ClusterByKeyField.ClusterByKeyField`

        :param field: the field we want to split in new symbols
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :param keyField: the field used as a key during the splitting operation
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :raise Exception if something bad happens

        """
        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")
        if keyField is None:
            raise TypeError("'keyField' should not be None")
        if not keyField in field.children:
            raise TypeError("'keyField' is not a child of 'field'")

        clusterByKeyField = ClusterByKeyField()
        return clusterByKeyField.cluster(field, keyField)
