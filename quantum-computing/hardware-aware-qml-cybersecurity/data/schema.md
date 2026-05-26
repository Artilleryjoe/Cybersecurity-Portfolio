# CSV Schemas

## URL dataset (`--dataset url`)
Required columns:
- `url` (string)
- `label` (int: 0 benign, 1 malicious)

## Email-header dataset (`--dataset email`)
Required columns:
- `spf_pass` (0/1)
- `dkim_pass` (0/1)
- `dmarc_pass` (0/1)
- `received_hops` (numeric)
- `domain_mismatch` (0/1)
- `interhop_delay_mean` (numeric)
- `ip_rep` (numeric, recommended [0,1])
- `domain_rep` (numeric, recommended [0,1])
- `label` (int: 0 benign, 1 anomalous)
