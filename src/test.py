from concurrent.futures import ProcessPoolExecutor

class MyClass:
    def manage_process(self, params):
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.method_to_run, params)
            future.result()  # Espera a que el proceso termine

    def method_to_run(self, params):
        print(f"Running with params: {params}")
        # Aquí va la lógica que consume memoria
        # Una vez que este método termina, el proceso se mata y se libera la memoria

if __name__ == "__main__":
    obj = MyClass()
    obj.manage_process("param1")
    obj.manage_process("param2")