# CipherEntropy

![CipherEntropy Logo](img/frieren_ascii.png)

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

- `--input`, `-i` - Input file path containing data to analyze
- `--output`, `-o` - Output file path for results (default: stdout)
- `--format`, `-f` - Output format: `json`, `csv`, `text` (default: text)

#### Cipher Options

- `--cipher`, `-c` - Cipher algorithm: `aes`, `des`, `rsa`, `chacha20` (default: aes)
- `--key-size` - Key size in bits (default: 256)
- `--algorithm`, `-a` - Specific algorithm variant

#### Analysis Options

- `--entropy-type` - Type of entropy calculation: `shannon`, `renyi`, `min-entropy` (default: shannon)
- `--block-size`, `-b` - Block size for analysis in bytes (default: 16)
- `--verbose`, `-v` - Enable verbose output
- `--statistical` - Include detailed statistical analysis

#### Advanced Options

- `--threads`, `-t` - Number of parallel processing threads (default: auto)
- `--iterations` - Number of iterations for entropy calculation (default: 1000)
- `--confidence-level` - Statistical confidence level (0-1, default: 0.95)
- `--help`, `-h` - Display help information
- `--version` - Display version information

## Example Commands

```bash
# Basic entropy analysis
cipherentropy --input data.bin --cipher aes

# Detailed statistical analysis with CSV output
cipherentropy -i encrypted.bin -o results.csv --format csv --statistical

# Custom cipher and entropy type
cipherentropy --input data.txt --cipher chacha20 --entropy-type renyi --verbose

# Process with multiple threads
cipherentropy -i large_file.bin -t 8 --iterations 5000
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

### Output Example

```json
{
  "file": "encrypted.bin",
  "cipher": "aes",
  "entropy": 7.94,
  "entropy_type": "shannon",
  "block_size": 16,
  "total_blocks": 1024,
  "statistics": {
    "mean": 7.94,
    "std_dev": 0.08,
    "min": 7.65,
    "max": 8.00
  }
}
```

## Requirements

- Python 3.8+ or Node.js 14+
- OpenSSL library
- NumPy (for statistical calculations)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or issues to the project repository.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

## Makefile Compilation

Add the following commands to your Makefile:

```makefile
gcc -O2 -Wall -fPIC -c des.c -o des.o
gcc -O2 -Wall -fPIC -c des_tables.c -o des_tables.o
gcc -shared -o libdes.so des.o des_tables.o
gcc -shared -fPIC rc4.c -o librc4.so
```
