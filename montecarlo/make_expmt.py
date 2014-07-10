# This asks the user for information and outputs a json file
import json

def main():        
    key, value = [], []
    key = ['total time', 'reactor time']
    sample={}
    num_iso = int(input('isotopes to enter: '))
    for i in range(num_iso):
        iso = input('isotope: ')
        quant = input('amount: ')
        sample.update({iso: quant})
    
    for i in key:
        value.append(input(i+': '))
    variables=dict(zip(key,value))
    
    var_stack = [variables, sample]
    # Write to json
    fname = input('output file: ') + '.json'
    
    with open(fname, 'w') as fname:
        json.dump(var_stack, fname, indent=2)

if __name__ == '__main__':
    main()
