import os
import csv
import time
from src.analysis.entropy import shannonEntropy
from src.visualization.plots import PlotGenerator
from src.analysis.frecuency import byte_frequency,byte_frequency_normalized
from src.analysis.dataset import Dataset
from src.crypto.des import DES
from src.crypto.rc4 import rc4_file
from src.crypto.aes import aes_encrypt_file, aes_decrypt_file
from src.crypto.shaCipher import sha256_file
from src.crypto.randomness import (
    generateTokenCiphers,
    generate_iv
)
# Run DES
des = DES()
def get_files(directory):
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    return sorted(files)
def generate_key_iv(cipher:str)-> tuple:
    if cipher == "DES":
        return generateTokenCiphers(cipher),generate_iv(cipher)
    elif cipher == "RC4":
        return generateTokenCiphers(cipher),None
    else:
        return generateTokenCiphers(cipher), generate_iv(cipher)
def to_hex(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.hex()

    return str(value)

def run_once(file_path:str,cipher:str, run_id:int):
    run_id +=1
    with open(file_path, "rb") as f:
        data = f.read()

    key, iv = generate_key_iv(cipher)

    entropy_raw = shannonEntropy(data)
    freq_raw = byte_frequency(data)
    sha_raw = sha256_file(file_path)
    
    if cipher == "DES":
        des.randKey(key)
        des.read_iv_file(file_path)
        start = time.perf_counter()
        des.encrypt_file(file_path)
        encrypt_time = (time.perf_counter() - start) * 1000
        with open(file_path + ".enc", "rb") as f:
            ciphertext = f.read()
        iv = des.read_iv_file(file_path+".enc")
        sha_enc = sha256_file(file_path+".enc")
        start = time.perf_counter()
        des.decrypt_file(file_path+".enc")
        decrypt_time = (time.perf_counter() - start) * 1000
        
    elif cipher == "RC4":
        start = time.perf_counter()
        rc4_file(file_path,file_path+".rc4",key)
        encrypt_time = (time.perf_counter() - start) * 1000
        with open(file_path + ".rc4", "rb") as f:
            ciphertext = f.read()
        sha_enc = sha256_file(file_path+".rc4")
        os.remove(file_path)
        start = time.perf_counter()
        rc4_file(file_path+".rc4",file_path,key)
        decrypt_time = (time.perf_counter() - start) * 1000
        os.remove(file_path+".rc4")
    elif cipher == "AES":
        start = time.perf_counter()
        aes_encrypt_file(file_path,file_path + ".aes",key,iv)
        encrypt_time = (time.perf_counter() - start) * 1000
        with open(file_path + ".aes", "rb") as f:
            ciphertext = f.read()
        os.remove(file_path)
        sha_enc = sha256_file(file_path+".aes")
        start = time.perf_counter()
        aes_decrypt_file(file_path+".aes",file_path,key,iv)
        decrypt_time = (time.perf_counter() - start) * 1000
        os.remove(file_path+".aes")

    #assert recovered == data
    freq_enc = byte_frequency_normalized(ciphertext)
    entropy_enc = shannonEntropy(ciphertext)
    
   


    return {
        "run_id": run_id,
        "algorithm": cipher,

        "file_name": os.path.basename(file_path),
        "size_bytes": len(data),

        "entropy_raw": entropy_raw,
        "entropy_encrypted": entropy_enc,
        "entropy_delta": entropy_enc - entropy_raw,

        "encrypt_time_ms": encrypt_time,
        "decrypt_time_ms": decrypt_time,

        "key": key,
        "iv": iv,

        "freq_raw": freq_raw,
        "freq_encrypted": freq_enc,

        "sha_raw": sha_raw,
        "sha_encrypted": sha_enc
    }


def run(conf):
    ds = Dataset()
    ds.init_files()
    files_ = get_files(conf["savedData"])
    if conf["algo"] == "All":
        algorithms = ["DES","RC4","AES"]
    else:
        algorithms =  [conf["algo"]]
    experiment_id = 1
    
    for algorithm in algorithms:
        for loop_id in range(conf["loops"]):
            for file_path in files_:
                result = run_once(
                    file_path=file_path,
                    cipher=algorithm,
                    run_id=experiment_id)
                ds.append_experiment([
                    experiment_id,
                    loop_id+1,
                    result["run_id"],
                    result["algorithm"],
                    result["file_name"],
                    result["size_bytes"],
                    result["entropy_raw"],
                    result["entropy_encrypted"],
                    result["entropy_delta"],
                    result["encrypt_time_ms"],
                    result["decrypt_time_ms"],
                    result["sha_raw"],
                    result["sha_encrypted"]
                ])
                ds.append_key([
                    result["run_id"],
                    result["algorithm"],
                    result["key"].hex(),
                    "" if result["iv"] is None else result["iv"].hex()
               ])
                experiment_id +=1
    plots = PlotGenerator(
        csv_file="data/csv/global.csv",
        output_dir=conf["savedPlot"]
    )
    plots.generate_all()
  
