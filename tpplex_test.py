import pytest
import tpplex
import subprocess
import shlex
import os, fnmatch

# test_cases = [
#     ("", "-k"), 
#     ("teste.c", "-k"), 
#     ("notexist.tpp", "-k"), 
#     ("lex-test-001.tpp", "-k"), 
#     ("lex-test-002.tpp", "-k"), 
#     ("lex-test-003.tpp", "-k"), 
#     ("lex-test-004.tpp", "-k"), 
#     ("lex-test-005.tpp", "-k"), 
#     ("lex-teste-006.tpp", "-k"), 
#     ("bubble_sort_2.tpp", "-k"), 
#     ("bubble_sort.tpp", "-k"), 
#     ("Busca_Linear_1061992.tpp", "-k"), 
#     ("buscaLinear-2020-2.tpp", "-k"), 
#     ("comp.tpp", "-k"), 
#     ("fatorial-2020-2.tpp", "-k"), 
#     ("fatorial.tpp", "-k"), 
#     ("fat.tpp", "-k"), 
#     ("fibonacci-2020-2.tpp", "-k"), 
#     ("fibonacci.tpp", "-k"), 
#     ("hanoi-2020-2.tpp", "-k"), 
#     ("insertionSort-2020-2.tpp", "-k"), 
#     ("insertSort-2020-2.tpp", "-k"), 
#     ("maiorDoVetor.tpp", "-k"), 
#     ("multiplicavetor.tpp", "-k"),
#     ("operacao_vetor-2020-2.tpp", "-k"), 
#     ("paraBinario-2020-2.tpp", "-k"), 
#     ("primo.tpp", "-k"), 
#     ("produtoEscalar.tpp", "-k"), 
#     ("prog_test.tpp", "-k"), 
#     ("sample.tpp", "-k"), 
#     ("selectionSort-2020-2.tpp", "-k"), 
#     ("selectionsort.tpp", "-k"), 
#     ("soma_maior_que_3.tpp", "-k"), 
#     ("somavet.tpp", "-k"), 
#     ("subtraiVetores.tpp", "-k"), 
#     ("verifica_valor_10.tpp", "-k"), 
#     ("verif_num_negativo.tpp", "-k"), 
#     ("bubble_sort-2020-2.tpp", "-k")
# ]

test_cases = [("", "-k"), ("teste.c", "-k"), ("notexist.tpp", "-k")]

files = fnmatch.filter(os.listdir('tests/'), '*.tpp')
for file in sorted(files):
    test_cases.append((file, "-k"))
    

@pytest.mark.parametrize("input_file, args", test_cases)
def test_execute(input_file, args):
    if(input_file != ''):
        path_file = 'tests/' + input_file
    else:
        path_file = ""
    
    # Por algum motivo quando passava input_file = "" o pytest passava um nome de arquivo e dava o erro:
    # b'ERR-LEX-NOT-TPP\n'
    # Expected output:
    # ERR-LEX-USE
    # process = subprocess.Popen(['python', 'tpplex.py', args, path_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd = "python tpplex.py {0} {1}".format(args, path_file)
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout, stderr = process.communicate()
    stdout, stderr

    path_file = 'tests/' + input_file
    output_file = open(path_file + ".lex.out", "r")

    #read whole file to a string
    expected_output = output_file.read()

    output_file.close()

    print("Generated output:")
    print(stdout)
    print("Expected output:")
    print(expected_output)

    assert stdout.decode("utf-8").strip() == expected_output.strip()