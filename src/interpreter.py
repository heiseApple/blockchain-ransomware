import importlib
from lark import Token
from lark.visitors import Interpreter

from blockchain_data_API import BlockchainDataAPI
import test_addr, test_tx
import utils 


class QueryInterpreter(Interpreter):
    """
    Interpreter class for querying and transforming data.
    """
    # TODO: NetworkX for creating a graph of tx and addr
    # TODO: _has_tx_one_output_higher_than_other as a query
    
    def __init__(self, debug_mode=False):
        super().__init__()
        self.debug_mode = debug_mode
        self.api = BlockchainDataAPI()
        
    def query(self, tree):
        """
        Process a query node.

        Args:
            tree: The tree structure for the current query starting from the current node.
            
        Returns:
            Result of visiting the children of the query node.
        """
        return self.visit_children(tree)
        
    def property(self, tree):
        """
        Process a property node.

        Args:
            tree: The tree structure for the current query starting from the current node.
            
        Returns:
            Result of visiting the children of the property node.
        """
        return self.visit_children(tree)
    
    def node_transaction(self, tree):
        """
        Process a transaction node and gather transaction data.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            The hash of the transaction.
        """
        self.tx_data = (
            self.api.get_transaction(tree.children[0].children[0].value) 
            if not self.debug_mode else test_tx.txs[0]
        )
        self._add_tx_properties()
        return self.tx_data['hash']
            
    def node_address(self, tree):
        """
        Process an address node and gather address data.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            The address hash.
        """
        self.addr_data = (
            self.api.get_address(tree.children[0].children[0].value)
            if not self.debug_mode else test_addr.addresses[0]
        )
        self._add_addr_properties()
        return self.addr_data['address']
        
    def transaction_prop(self, tree):
        """
        Process a transaction property node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            Result of property checking.
        """
        return self._prop_checker(tree)
        
    def address_prop(self, tree):
        """
        Process an address property node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            Result of property checking.
        """
        return self._prop_checker(tree)
        
    def transaction_expression(self, tree):
        """
        Process a transaction expression node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            Result of expression checking.
        """
        eval_res =  self._expression_checker(tree)
        utils.print_node('Transaction expression:', tree, eval_res)
        return eval_res
    
    def address_expression(self, tree):
        """
        Process an address expression node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            Result of expression checking.
        """
        eval_res =  self._expression_checker(tree)
        utils.print_node('Address expression:', tree, eval_res)
        return eval_res
    
    def _prop_checker(self, tree):
        """
        Check properties based on the provided tree structure.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            Boolean result based on property evaluation.
        """
        # If there is only one child left return the output value of the child
        if len(tree.children) == 1 and tree.children[0].data in ['transaction_expression', 'address_expression']:
            return self.visit_children(tree)
        
        # If the structure is a parenthesized expression (e.g., (expression)), visit the child node.
        elif tree.children[0] == '(' and tree.children[2] == ')':
            
            for i, child in enumerate(tree.children):
                if not isinstance(child, Token):
                    return utils.get_boolean(self.visit(child))
                
        else:    
                
            Operator = getattr(
                importlib.import_module('operators'), tree.children[1 if tree.children[1] == 'And' else 0]
            )
            operator = Operator()
            
            return operator.eval(tree.children, self)


    def _expression_checker(self, tree):  
        """
        Check expressions based on the provided tree structure.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            Result of expression evaluation.
        """
        left_child = self.visit_children(tree)[0]

        if isinstance(left_child, Token):
            # Run 'IN' operation -> left op is a hash or address, right op is the list of input or outputs
            return tree.children[1].value in self.visit_children(tree)[3]

        operator = tree.children[1]
        right_child = self.visit_children(tree)[-1]
        left_child, right_child = utils.cast_for_eval([left_child, right_child])
        
        if operator == '=':
            # If the expression contains 'HEX' or 'IP', select the last child on the right as right_value
            return left_child == right_child

        if operator == '<':
            return left_child < right_child

        if operator == '>':
            return left_child > right_child

        raise Exception("Unsupported operator")
        
    def get_tx_atom(self, tree):   
        """
        Process a transaction atom node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            The value of the transaction relative to the field specified by tx atom
        """     
        return self.tx_data[tree.children[0]]
    
    def get_tx_atom_by_index(self, tree):   
        """
        Process a transaction atom node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            The value of the transaction relative to the field specified by tx atom
        """     
        return self.tx_data[tree.children[0]][int(tree.children[1])]
    
    # TODO: rename as get_addr ...
    def address_atom(self, tree):
        """
        Process an address atom node.

        Args:
            tree: The tree structure for the current query starting from the current node.

        Returns:
            The value of the address relative to the field specified by addr atom
        """
        return self.addr_data[tree.children[0]]
    
    # TODO: if tx or addr doesn't exist stop iterating
    def _move_to_next_tx(self, iter):
        """
        Moves to the next transaction in the sequence.

        Args:
            iter: The current iteration index.
        """
        if not self.debug_mode:
            self.addr_data = self.api.get_address(self._find_highest_out_addr())
            self.tx_data = self.api.get_transaction(self._find_highest_out_tx())
        else:
            self.addr_data = test_addr.addresses[iter]
            self.tx_data = test_tx.txs[iter+1]
        self._add_tx_properties()
        
    def _move_to_next_addr(self, iter):
        """
        Moves to the next address in the sequence.

        Args:
            iter: The current iteration index.
        """
        if not self.debug_mode:
            self.tx_data = self.api.get_transaction(self._find_highest_out_tx())
            self.addr_data = self.api.get_address(self._find_highest_out_addr())
        else:
            self.tx_data = test_tx.txs[iter]
            self.addr_data = test_addr.addresses[iter+1]
        self._add_addr_properties()
        
    def _add_tx_properties(self):
        """
        Adds properties to the current transaction data.
        """
        # Add num inputs and output
        self.tx_data['num_inputs'] = len(self.tx_data.get('inputs'))
        self.tx_data['num_outputs'] = len(self.tx_data.get('out'))
        
        # TODO: add as a key out_value_1 _2
        # Add total BTC received and sent to the tx
        self.tx_data['total_rec'] = sum(
            [i.get('prev_out').get('value') for i in self.tx_data.get('inputs')]
        ) / 1e8 
        self.tx_data['total_sent'] = sum(
            [o.get('value') for o in self.tx_data.get('out')]
        ) / 1e8 
        self.tx_data['sent_values'] = [
            o.get('value')/1e8  for o in self.tx_data.get('out')
        ]
        self.tx_data['rec_values'] = [
            i.get('prev_out').get('value')/1e8 for i in self.tx_data.get('inputs')
        ]
        self.tx_data['out_addresses'] = [
            o.get('addr') for o in self.tx_data.get('out')
        ]
        self.tx_data['in_addresses'] = [
            i.get('prev_out').get('addr') for i in self.tx_data.get('inputs')
        ]
        
    def _add_addr_properties(self):
        self.addr_data['out_txs_hash'] = [
            i.get('hash') for i in self.addr_data.get('txs') if i.get('result') < 0
        ]
        self.addr_data['in_txs_hash'] = [
            i.get('hash') for i in self.addr_data.get('txs') if i.get('result') >= 0
        ]
        
    def _find_highest_out_addr(self):
        """
        Find the address with the highest output value.

        Returns:
            The hash of the address with the highest output value.
        """
        addrs = self.tx_data.get('out', [])
        max_addr = max(addrs, key=lambda addr: addr.get('value', 0), default=None)
        max_addr_hash = max_addr.get('addr') if max_addr else None
        return max_addr_hash
    
    def _find_highest_out_tx(self):
        """
        Find the transaction with the highest output value.

        Returns:
            The hash of the transaction with the highest output value.
        """
        txs = self.addr_data.get('txs', [])
        max_tx = min(txs, key=lambda tx: tx.get('result', 0), default=None)
        max_tx_hash = max_tx.get('hash') if max_tx else None
        return max_tx_hash    