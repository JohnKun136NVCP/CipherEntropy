# CipherEntropy

![CipherEntropy Logo](img/frieren_ascii.png)

Created by [JohnKun136NVCP](https://github.com/JohnKun136NVCP)

Project to get my balchor degree on physics and computer science, and to learn more about cryptography and entropy analysis.

## Project Overview

CipherEntropy is a cryptographic tool designed to analyze and measure the entropy of encrypted data. It provides comprehensive CLI configurations and execution options for security researchers, cryptographers, and developers who need to evaluate the randomness and cryptographic strength of cipher outputs.

## Features

- **Entropy Analysis**: Calculate Shannon entropy and other entropy metrics for encrypted data
- **Cipher Support**: Support for multiple cipher algorithms
- **Statistical Analysis**: Detailed statistical breakdown of encryption results
- **CLI Integration**: Flexible command-line interface with multiple configuration options
- **Output Formats**: Multiple output format options for analysis results

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Basic Execution

```bash
cipherentropy --input <file> --output <file>
```

### CLI Configuration Options

#### Input/Output Options

- `-n`, Run with n loops (default: 1)
- `-al`, Run with specific algorithm (default: all)
- `-i`, Show or hide prompt (default: show)
- `-sd`, Change directory of data (default: ./data)
- `-sp`, Change directory of plots (default: ./data/plots)
- `-rc`, Reset default configuration on config.json (default: False)
- `-op`, Only plots default data (default: False)
- `-r`, Run program (default: False)



## Example Commands

For example, you can run the following commands to analyze encrypted files:

```bash
# Basic entropy analysis
python3 main.py -n 1000 -al aes -r

# With specific input and output files
python3 main.py -i input.txt -sp /home/user/plots -r

# If you want to reset the configuration to default
python3 main.py -rc True

```

## Hex Representation

```
63 69 70 68 65 72 65 6e 74 72 6f 70 79
```

## Results Interpretation

### Shannon Entropy

Values range from 0 to 8 (for 8-bit data):
- **0-2**: Low entropy (non-random, weak encryption)
- **2-6**: Moderate entropy (acceptable encryption)
- **6-8**: High entropy (strong encryption, good randomness)

### Configuration Example

```json
{
  "loops": 1,
  "algo": "All",
  "show": true,
  "savedData": "/path/to/data",
  "savedPlot": "/path/to/plots",
  "onplots": false
}
```

## Requirements

- Python 3.8+ or Node.js 14+
- OpenSSL library
- NumPy (for statistical calculations)
- Matplotlib (for plotting results)
- SciPy (for advanced statistical analysis)
- Pandas (for data manipulation)


## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or issues to the project repository.

## Support

For issues, questions, or suggestions, please open an issue on the project repository. Connect with the telegram that is available on my github profile.

## Makefile Compilation

Add the following commands to your Makefile:

```makefile
gcc -O2 -Wall -fPIC -c des.c -o des.o
gcc -O2 -Wall -fPIC -c des_tables.c -o des_tables.o
gcc -shared -o libdes.so des.o des_tables.o
gcc -shared -fPIC rc4.c -o librc4.so
```
