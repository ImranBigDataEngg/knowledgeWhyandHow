# Contributing

## A first contribution

- Port the reconciliation query to PostgreSQL or SQL Server. Include a script to load the fixture and demonstrate the same winners, rejects, and summary.
- Add a second fixture that exercises all validation boundaries. State the expected row IDs and reason codes before implementing the assertions.
- Run a vendor walkthrough and improve a step that was hard to reproduce. Include the product version, the relevant setting, and the observed fixture output.

For a new lab, open an issue with the question you want to answer, a small input example, and the expected outcome. For a bug, include the version, the command or mapping steps, and the smallest synthetic input that reproduces it.

## Prepare a pull request

1. Fork the repository and create a branch for one change.
2. Use synthetic fixtures and document how to reproduce the result from a fresh clone. For parity changes, compare the winning row IDs and reject reasons as well as the totals.
3. Run the relevant checks from the repository root.

   ```sh
   python -m unittest discover -s tests -p test_order_reconciliation.py -v
   ```

   If you change the Spark path or the shared contract, [run the Spark suite](labs/order_reconciliation/README.md#run-with-pyspark). Follow the [full test setup](README.md#quick-start) for the CSV quality checker and changes that span multiple examples.

4. Open a pull request that explains the behavior, the affected tools and versions, and the checks you ran. For a guide, label steps that require a licensed or cloud environment.

All contributed material must be yours to share under the [project license](LICENSE). Cite external references in guides. Use synthetic data and placeholder account, workspace, and storage names in examples.
