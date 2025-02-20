from lark import Lark

from interpreter import QueryInterpreter


def main():
    with open("grammar.lark") as f:
        lark_parser = Lark(f, parser="lalr")

    # Test queries
    test_queries = [
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Transaction.num_outputs = 2",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Transaction.size = 225",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Transaction.size = 225 And Transaction.num_outputs = 2 And Transaction.time > 1664289786 And Transaction.lock_time = 755925",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check (Transaction.size = 225 And (Transaction.time > 1664289786 And Transaction.num_outputs = 2))",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Gtrans 3 Transaction.size = 225 And Transaction.num_outputs = 2 And Transaction.time > 1664289786 And Transaction.lock_time > 755924"
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Ftrans 3 Transaction.size = 226 And Transaction.num_outputs = 2"
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check (Transaction.size > 220 And Transaction.size < 280) And (Transaction.num_outputs = 2)",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check (Not (Transaction.size > 220 And Transaction.size < 280)) And (Not Transaction.num_outputs = 2)",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Transaction.hash = HEX 1231231a0714f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Transaction.relayed_by = IP 0.0.0.0",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Not Transaction.double_spend = False",
        # "From Address bc1qram93t5yppk9djr8a4p4k0vregdehnzcvp9y40 Check Address.address = HEX bc1qram93t5yppk9djr8a4p4k0vregdehnzcvp9y40",
        # "From Address bc1qram93t5yppk9djr8a4p4k0vregdehnzcvp9y40 Check Xtrans Transaction.size > 220",
        # "From Address bc1qram93t5yppk9djr8a4p4k0vregdehnzcvp9y40 Check Gaddr 3 (Address.n_tx > 1 And Not Address.total_sent < 10000)",
    # "From Address bc1qram93t5yppk9djr8a4p4k0vregdehnzcvp9y40 Check Faddr 3 (Address.n_tx > 1 And Address.total_sent > 10000) And Address.final_balance > 0",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check HEX 1KeNiiR3BZT8GPqQ61ihmvwRMsCQtcXNYC in Transaction.out_addresses",
        # "From Address bc1qram93t5yppk9djr8a4p4k0vregdehnzcvp9y40 Check HEX 23528e9e9335fa05eee083ba326abe7058c3b489962707204162a7b9b87c8da0 in Address.out_txs_hash",
        # "From Transaction 7a51a014f6bd3ccad3a403a99ad525f1aff310fbffe904bada56440d4abeba7f Check Transaction.sent_values[0] > Transaction.sent_values[1]",
    ]


    """ # after 8/5/2021 00:00:00 -> 1620432000
    # Colonial Pipeline
    test_queries = [
        "From Transaction 6a798026d44af27dbacd28ea21462808df8deca51794cec80c1b59e07ef924a2 Check Transaction.num_inputs = 2 And Transaction.total_rec > 170 And Transaction.time > 1620432000"
    ] """
        
    for tq in test_queries:
        parsed_query = lark_parser.parse(tq)
        node, query_result = QueryInterpreter(debug_mode=True).visit(parsed_query)
        # query_result = list(itertools.chain(*query_result))[0] #TODO: return only a boolean value
        print('='*100)
        print(f'Query result for node {node}:\n {query_result}') # .pretty()
        # NOTE: To print the AST, we need to import "from lark import tree" and do this step without a transformer class.
        # tree.pydot__tree_to_png(lark_parser.parse(tq), f"query_{i}.png")


if __name__ == "__main__":
    main()