from Bio import SeqIO, pairwise2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def align_sequences(seq1, seq2):
    alignments = pairwise2.align.globalxx(seq1, seq2)
    print(f"\nAlignment results for '{seq1}' and '{seq2}':")
    for i, aln in enumerate(alignments):
        print(f"Alignment {i+1}:\n{aln}")
    return alignments

def plot_data(data):
    plt.figure(figsize=(6,4))
    plt.plot(data, marker='o', color='green')
    plt.title('Biological Data Visualization')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()

def analyze_statistics(data):
    mean = np.mean(data)
    std = np.std(data)
    print(f"\nStatistical Analysis:\nMean: {mean:.2f}\nStd Dev: {std:.2f}")
    return mean, std

def main():
    print("Bioinformatics Data Analysis")
    # Example DNA sequences
    seq1 = "ACTGACCTGA"
    seq2 = "ACCGTCTGA"
    alignments = align_sequences(seq1, seq2)

    # Example biological data (e.g., gene expression levels)
    data = np.random.normal(loc=10, scale=2, size=20)
    print(f"\nSample biological data:\n{data}")
    plot_data(data)

    # Statistical analysis
    mean, std = analyze_statistics(data)

    # Example: Load FASTA file (uncomment and provide file path to use)
    # for record in SeqIO.parse('example.fasta', 'fasta'):
    #     print(record.id, record.seq)

    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()
