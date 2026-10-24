"""
Validators Registry: Curated target validators on Solana Mainnet spanning
three distinct client software / forks:
1. Jito-Solana (v4.3.2) - MEV Auction integrated leader scheduler
2. Firedancer / Frankendancer (v26.10.4) - Jump Crypto C/C++ tile pipeline
3. Agave / Next-gen Alpha (v4.3.0 / v4.5.0-alpha.2) - Anza / Community fork
"""

TARGET_VALIDATORS = [
    {
        "id": "shinobi_jito",
        "moniker": "Shinobi Systems",
        "node_pubkey": "Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk",
        "vote_pubkey": "CcaHc2L43ZWjwCHART3oZoJvHLAe9hzT2DJNUpBzoTN1",
        "client_family": "Jito-Solana",
        "client_version": "4.3.2",
        "activated_stake_sol": 17133144,
        "sample_analyzed_slot": 460184800
    },
    {
        "id": "kraken_jito",
        "moniker": "Kraken",
        "node_pubkey": "krakeNd6ednDPEXxHAmoBs1qKVM8kLg79PvWF2mhXV1",
        "vote_pubkey": "krakens1DeFegz34wHhU893e1b7xLzGv7r8eJvPqPqP",
        "client_family": "Jito-Solana",
        "client_version": "4.3.2",
        "activated_stake_sol": 4079218,
        "sample_analyzed_slot": 460184876
    },
    {
        "id": "jd549_firedancer",
        "moniker": "JD549-Firedancer",
        "node_pubkey": "JD549HsbJHeEKKUrKgg4Fj2iyv2RGjsV7NTZjZUrHybB",
        "vote_pubkey": "3JD3jMmnR6g88qff2WZ3cMHJRjJMUk9yVZtmYTYeFrXf",
        "client_family": "Firedancer",
        "client_version": "26.10.4",
        "activated_stake_sol": 6606828,
        "sample_analyzed_slot": 460184832
    },
    {
        "id": "awesome_firedancer",
        "moniker": "Awesome-FD",
        "node_pubkey": "Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM",
        "vote_pubkey": "DumiCKHVqoCQKD8roLApzR5Fit8qGV5fVQsJV9sTZk4a",
        "client_family": "Firedancer",
        "client_version": "26.10.4",
        "activated_stake_sol": 7002101,
        "sample_analyzed_slot": 460184856
    },
    {
        "id": "revtec_firedancer",
        "moniker": "Revtec-FD",
        "node_pubkey": "revtecFsGSRCdF29atQvchSXrjwBesA9vSisD4fyH5K",
        "vote_pubkey": "revtec7vL39V1aY4q5Z6W7E8R9T0Y1U2I3O4P5A6S7D",
        "client_family": "Firedancer",
        "client_version": "26.10.4",
        "activated_stake_sol": 2514800,
        "sample_analyzed_slot": 460184872
    },
    {
        "id": "validator_9rkj_agave",
        "moniker": "Validator-9rkJ",
        "node_pubkey": "9rkJMARqK6VBkcxGfKBAwnA44gPAfGxPbPsfsggFNDSQ",
        "vote_pubkey": "HimWQUK61d9wxhw7EYu9jUje7xQiDs4jKexaTSvuCmXE",
        "client_family": "Agave/Jito-4.3.0",
        "client_version": "4.3.0",
        "activated_stake_sol": 4723045,
        "sample_analyzed_slot": 460184812
    }
]

# Canonical Jito Tip Accounts used to isolate off-chain MEV auction bundles
# from pure scheduler ordering
JITO_TIP_ACCOUNTS = {
    "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
    "HFqU5x63VTxvQssQn1Wn78zsRtDHVKBy36Ba2zQuwhKA",
    "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
    "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
    "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
    "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
    "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
}
