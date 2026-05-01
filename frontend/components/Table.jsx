import React from "react";

export default function Table({ columns, rows, actionLabel, onAction }) {
  return (
    <section className="panel table-panel">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
            {onAction ? <th>Action</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.length > 0 ? (
            rows.map((row) => (
              <tr key={row.id}>
                {row.values.map((value, index) => (
                  <td key={`${row.id}-${columns[index]}`}>{value}</td>
                ))}
                {onAction ? (
                  <td>
                    <button
                      type="button"
                      className="table-action danger-action"
                      onClick={() => onAction(row)}
                    >
                      {actionLabel ?? "Remove"}
                    </button>
                  </td>
                ) : null}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length + (onAction ? 1 : 0)} className="table-empty">
                No records available yet.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
