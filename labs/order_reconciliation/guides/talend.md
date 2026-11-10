# Reconcile orders in Talend Studio 8

Build a Standard Job with the [sample CSV](../data/order_events.csv). This mapping uses the same [validation order and winner rule](../README.md#reconciliation-rule) as the local engines. Use the local loader to preflight a new file's structure and source IDs before running the mapping exercise.

1. Add `tFileInputDelimited`. Use UTF-8, comma separators, one header row, and CSV options with double quotes for enclosure and escape. Define `row_id`, `revision`, and `amount_cents` as Long fields and `order_id` and `status` as String fields. Allow empty revision and amount values to enter as null. [tFileInputDelimited properties](https://help.qlik.com/talend/en-US/components/8.0/delimited/tfileinputdelimited-standard-properties).
2. Connect it to `tMap` and name the input link `event`. Define the String variable `order_key` first, followed by the String variable `reason`.

   ```java
   // order_key
   event.order_id == null ? "" : event.order_id.replaceAll("^ +| +$", "")

   // reason
   Var.order_key.isEmpty() ? "missing_order_id"
       : event.revision == null || event.revision < 1 || event.revision > 999999 ? "invalid_revision"
       : !("OPEN".equals(event.status) || "PAID".equals(event.status)
           || "CANCELLED".equals(event.status)) ? "invalid_status"
       : event.amount_cents == null || event.amount_cents < 0
           || event.amount_cents > 1000000000L ? "invalid_amount"
       : null
   ```

3. Configure two `tMap` outputs. Use `Var.reason == null` for `valid_events` with all five fields, mapping `order_id` to `Var.order_key`. Use `Var.reason != null` for `rejected_events` with `row_id` and `reason`. Connect the reject output to a delimited file.
4. Send `valid_events` through `tSortRow`. Sort by `order_id` ascending, `revision` descending, and `row_id` descending. Set the two numeric sort keys to numeric comparison. Connect to `tUniqRow` with `order_id` as the sole key, enable **Case sensitive**, and keep the **Uniques** link. That link emits the first row seen for each key, so the sort controls the winner. Install `tUniqRow` with Feature Manager if needed. [tSortRow properties](https://help.qlik.com/talend/en-US/components/8.0/processing/tsortrow-standard-properties) · [Uniques and Duplicates links](https://help.qlik.com/talend/en-US/studio-user-guide/8.0-R2025-05/row-connection) · [tUniqRow](https://help.qlik.com/talend/en-US/components/8.0/processing/tuniqrow).
5. Use `tReplicate` to send the winners both to a delimited file and to a paid summary branch. On that branch, use `tFilterRow` with an **Equals** condition on `status` and the value `"PAID"`. Then use `tAggregateRow` with no grouping keys to count `row_id` and sum `amount_cents`. Store the sum in a Long field.

Compare the five winning IDs `3, 5, 8, 14, 16` and the six rejected IDs and reason codes with [expected.json](../data/expected.json). The paid summary should contain three orders and 3,899 cents. As a check on the design, move the paid filter before `tUniqRow`, rerun the sample, and find the cancellation that the earlier filter removes.
