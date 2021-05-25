from code import encode
from decode import decode


def main():
    print("Welcome to Hu-Tucker archiver.\nDeveloped by Alex Borzikov aka Borlehandro.")
    mode = input("Enter \"code\" to encoding or \"decode\" to decoding\n")
    if mode == "code":
        in_filename = input("Enter input filename:")
        out_filename = input("Enter output filename (without extension):")
        encode(in_filename, out_filename)
    elif mode == "decode":
        in_filename = input("Enter input filename (with .huta extension):")
        out_filename = input("Enter output filename (with original file extension):")
        decode(in_filename, out_filename)


if __name__ == "__main__":
    main()
