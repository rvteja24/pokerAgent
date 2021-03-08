import _pickle as pickle


class HelperClass:
    # to be used while updating trees after each game during training
    @staticmethod
    def update_tree(tree, tree_name):
        with open(tree_name, 'wb') as file:
            file.write(pickle.dumps(tree))
