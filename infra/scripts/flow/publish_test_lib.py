from infra.scripts.flow.publish import Publish


class Test_lib(Publish):
    def __init__(self,file_path):
        super().__init__(file_path)

    def run(self):

        pass

    def get_c_test_lib(self):
        pass
    def get_uvm_test_lib(self):
        pass

    def publish_share_command(self):
        pass

    def publish_each_test_command(self):
        pass

    def test_is_child(self,test_name):
        pass
    def test_is_parent(self,test_name):
        pass


def main():
    pass

if __name__ == "__main__":
    main()