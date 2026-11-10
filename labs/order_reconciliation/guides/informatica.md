# Reconcile orders in Informatica Cloud Data Integration

Use a standard mapping with a flat file connection and a Secure Agent that can read the [fixture CSV](../data/order_events.csv). The example uses the Rank transformation, which requires an edition that includes it. Use the local loader to preflight a new file's structure and source IDs before running the mapping exercise. [Informatica Cloud Data Integration transformation guide](https://docs.informatica.com/content/dam/source/GUID-2/GUID-2B5E2342-3D75-4BCE-B092-A78F85631717/31/en/CDI_October2021_Transformations_en.pdf).

1. Add a **Source** transformation using the CSV with column names from the first row. Set `order_id` and `status` to String. Use signed 64-bit integer or decimal with scale 0 for `row_id`, `revision`, and `amount_cents`. Read empty numeric fields as null.
2. Use an **Expression** transformation to derive a String variable named `order_key` as `LTRIM(RTRIM(order_id))`. Expose the normalized key in an output field such as `normalized_order_id`. Derive a String output `reason` from the following expression.

   ```text
   IIF(ISNULL(order_key) OR LENGTH(order_key) = 0, 'missing_order_id',
       IIF(ISNULL(revision) OR revision < 1 OR revision > 999999, 'invalid_revision',
           IIF(ISNULL(status) OR (status != 'OPEN' AND status != 'PAID' AND status != 'CANCELLED'),
               'invalid_status',
               IIF(ISNULL(amount_cents) OR amount_cents < 0 OR amount_cents > 1000000000,
                   'invalid_amount', 'ok'))))
   ```

3. Add a **Router** with a `Valid` group using `reason = 'ok'`. Route the default output to the rejected target with `row_id` and `reason`.
4. On the `Valid` branch, add an **Expression** with `rank_key = revision * 1000000 + row_id`. Use a 64-bit or Decimal field with at least 12 digits and scale 0. The source sequence is less than one million, so a higher revision always wins and `row_id` breaks ties within a revision.
5. Use **Rank** with **Top**, **Number of Ranks** `1`, rank field `rank_key`, and group field `normalized_order_id`. Connect the winners to a current-orders target and map `normalized_order_id` back to `order_id`.
6. From the Rank output, add a **Filter** for `status = 'PAID'` and an **Aggregator** with no group fields. Compute `COUNT(row_id)` as `paid_orders` and `SUM(amount_cents)` as `paid_cents`. Use a 64-bit or Decimal output for the amount.

Run the mapping task and compare both detail targets and the summary with [expected.json](../data/expected.json). Check `ORD-300` first. It should select row 8 for 2,600 cents, even if you reverse the input row order. Check that `ORD-200` ends as `CANCELLED` and contributes zero to the paid total.
