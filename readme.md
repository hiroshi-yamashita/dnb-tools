# DNB (Dynamical Network Biomarker) Analysis

DNB (Dynamical Network Biomarker) analysis targets detecting early warning signals with collective fluctuations at pre-disease states before critical transitions from healthy states to disease states [1, 2, 3].

 This repository has two tools for DNB analysis:

- DNB tool for tabular data
- DNB tool for timeseries data

 Use the appropriate one, depending on the type of data you want to analyze.

# Requirements

```code
python>=3.9
numpy
scipy
pandas
matplotlib
sklearn
ruptures
tqdm
PyYAML
```

# Usage

You can try the analysis on Google Colaboratory. Please refer to these notebooks for detailed usage.

- **DNB tool for tabular data** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hiroshi_yamashita/dnb-tools/blob/master/tutorial_dnb_tabulars.ipynb)
- **DNB tool for timeseries data** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hiroshi_yamashita/dnb-tools/blob/master/tutorial_dnb_timeseries.ipynb)

If you have python environment, you can use the program by cloning the project by

```
git clone https://github.com/hiroshi-yamashita/dnb-tools.git
```

or by downloading the zip file from `<> Code` button above.

## References

1. L. Chen, R. Liu, Z.-P. Liu, M. Li, and K. Aihara: “Detecting Early-warning Signals for Sudden Deterioration of Complex Diseases by Dynamical Network Biomarkers,” Scientific Reports, 2, 342, 1-8, doi:10.1038/srep00342 (2012).
1. M. Oku and K. Aihara, “On the Covariance Matrix of the Stationary Distribution of a Noisy Dynamical System,” Nonlinear Theory and Its Applications, IEICE, 9(2), 166-184, doi:10.1587/nolta.9.166 (2018).
1. K. Aihara, R. Liu, K. Koizumi, X. Liu, and L. Chen: “Dynamical Network Biomarkers: Theory and Application,” Gene, 808, 145997, 1-10, doi: 10.1016/j.gene.2021.145997 (2022).

The sample data in `datasets/data/` is from the following:
<https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE77578>

## Cite

```code
@article{Makito Oku2019,
  title={Two Novel Methods for Extracting Synchronously Fluctuated Genes},
  author={Makito Oku},
  journal={IPSJ Transactions on Bioinformatics},
  volume={12},
  number={ },
  pages={9-16},
  year={2019},
  doi={10.2197/ipsjtbio.12.9}
}
```

## License

Apache License 2.0

## Author

Hiroshi Yamashita(h.yamashita@ist.osaka-u.ac.jp), Yuji Okamoto(yuji.0001@gmail.com), Makito Oku(oku@inm.u-toyama.ac.jp)
