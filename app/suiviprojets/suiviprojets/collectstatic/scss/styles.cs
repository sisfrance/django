/* Error: Undefined variable.
 *   ,
 * 2 |     background-color: $body-color;
 *   |                       ^^^^^^^^^^^
 *   '
 *   main.scss 2:23  root stylesheet */

body::before {
  font-family: "Source Code Pro", "SF Mono", Monaco, Inconsolata, "Fira Mono",
      "Droid Sans Mono", monospace, monospace;
  white-space: pre;
  display: block;
  padding: 1em;
  margin-bottom: 1em;
  border-bottom: 2px solid black;
  content: "Error: Undefined variable.\a   \2577 \a 2 \2502      background-color: $body-color;\d\a   \2502                        ^^^^^^^^^^^\a   \2575 \a   main.scss 2:23  root stylesheet";
}
