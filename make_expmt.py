# This asks the user for information and outputs a json file
import json

def main():        
    key, value = [], []
    key = ['megawh', 'mass (g)',
           'molar mass', 'abundance', 'half life']
    for i in key:
        value.append(input(i+': '))
    variables=dict(zip(key,value))
        
    # Write to json
    fname = variables['element'] + '.json'
    
    with open(fname, 'w') as fname:
        json.dump(variables, fname, indent=2)

if __name__ == '__main__':
    main()
