# ARTSS

## Overview

Airport Runway and Taxiway Simulation System

This repository hosts the source code for Group 6's SE 300 project.

## Getting Started

1. Clone the repository

```sh
git clone https://github.com/cfrankovich/ARTSS.git
```

2. Navigate into the repository and install requirements

```sh
cd ARTSS
pip install -r requirements.txt
```

3. Run the program

```sh
python main.py
```

## Contributing

### Branch Structure

-   **`main` branch:** After every sprint, the stable version of our code from the `dev` branch is merged into `main`.
-   **`dev` branch:** This serves as our active development branch. All ongoing work the next release is merged here.
-   **`feature/<feature-name>` feature branches:** For every new feature or significant change, create a new branch off `dev` using the naming convention `feature/<feature-name>`.

### Workflow Summary

1. **Starting a New Feature:**

-   Branch out from `dev` with a new `feature/<feature-name>` branch for your work.

2. **Integrating a Feature:**

-   Once your feature is complete and tested, submit a pull request to merge your `feature/<feature-name>` branch back into `dev`.

3. **Releasing:**

-   At the end of each sprint, `dev` is merged into `main`, marking a new release.
