# Biomass Dashboard Data

This repository contains the configuration for the [Biomass Dashboard API](https://github.com/MAAP-Project/biomass-dashboard-api) datasets, products, and country pilots. 

## Deployment

We use environment branches for deployments:

- `main`: [biomass.dit.maap-project.org](https://biomass.dit.maap-project.org)

- `staging`: [biomass.staging.maap-project.org](https://biomass.staging.maap-project.org)

- `production`: [biomass.maap-project.org](https://biomass.maap-project.org)

## Development

Maintaining compatible git histories between the three environment branches can be challenging but here are some rules to follow when working on new features or deploying hotfixes:

### Feature Development
- **Feature branches → main**: Use **Squash and merge** for clean, single-commit features

### Branch Promotions  
- **main → staging**: Use **Create a merge commit** (required)
- **staging → production**: Use **Create a merge commit** (required)

### Hotfixes & Backports
- **staging/production → main**: Use **Create a merge commit** to preserve branch relationships
- **Never** use squash or rebase for backports - it breaks future merges

### Key Principle
- **Squash**: Only for feature branches going into main
- **Merge commit**: Always for branch-to-branch promotions and backports
- **Never mix strategies** for promotion/backport workflows

### Sync Rule
- **No need to sync staging → main** if differences are only promotion merge commits
- **Only sync** if staging/production have direct commits (hotfixes, config changes)

## Configuration

For each of these entity types, the pattern is to create a config file or files for that entity, and then
put the `id` value in the config.yml file. Note that in other versions of the dashboard, the values in config.
yaml might be the prefix or entire name of the json files, but in this project, it always the `id` used within the json file.

### Datasets

The `datasets` directory contains a directory for the available datasets. Each dataset is a `json` file (see example: [datasets/NCEO_Africa.json](./datasets/NCEO_Africa.json))

Each dataset ID (*not* the name of the file) must be included in the `DATASETS` array in [config.yml](config.yml). 

### Products

The `products` directory contains a directory for each product. Within each directory, there are two files:
1. a json file containing the definition of the product
2. `summary.html` - an HTML fragment that's used as the summary description in the dashboard

Each product ID (*not* the name of the file) must be included in the `PRODUCTS` array in [config.yml](config.yml). 

The `global` product is used for the All or Global product in the dashboard.

### Country Pilots

The `country_pilots` directory contains a directory for each country pilot. Within each directory, there are two files:
1. a json file containing the definition of the country pilot
2. `summary.html` - an HTML fragment that's used as the summary description in the dashboard

Each country pilot ID (*not* the name of the file) must be included in the `COUNTRY_PILOTS` array in [config.yml](config.yml). 

## Usage

### Execution via GitHub Actions

By default, these dashboard api configuration files will be deployed to S3 via a GitHub Action. These will
be deployed for the branches main, staging, and production.

To configure this:

1. In the GitHub repository, add secrets (Settings -> Secrets) for accessing AWS (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
2. Update config.yml with the appropriate BUCKET configuration.
3. Push config.yml to GitHub and verify it runs correctly. Note only branches configured in `.github/workflows/update-datasets-and-sites.yml` will run the workflow (generate the datasets/sites metadata files).

### Manual Execution

If you wish to deploy manually, e.g., to test using a custom stage named for you.

This will create and copy the configuration files to the S3 location indicated in `BUCKET` and print the final JSON description.

1. Update config.yml with the appropriate BUCKET configuration
2. Export a shell variable for `STAGE`, e.g., `export STAGE=pvarner`
3. Run the generators.

```bash
export STAGE=local
python dataset_metadata_generator/src/main.py | jq .
python products_metadata_generator/src/main.py | jq .
python country_pilots_metadata_generator/src/main.py | jq .
```

