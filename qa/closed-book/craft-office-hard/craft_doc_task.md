TASK — build ONE batch script that creates a fully formatted document.

You have two ways to use WordCraft (use whichever you prefer):
 (A) the `wordcraft__execute` / `wordcraft__batch` MCP tools, OR
 (B) the CLI: write a JSON script file and run
     <APPS>\CraftSuiteApps\WordCraft\wordcraft-cli.exe run --script <file>

Either way, produce ONE batch of commands that creates a document and saves it to
exactly: <REPO>\qa\closed-book\craft-office-hard\craft-hard-result.docx

The document must contain ALL of the following (use these exact command IDs,
which are confirmed to exist):
  file.new, text.insert, para.heading1, para.heading2, format.bold, format.italic,
  format.color (params: {"color":"RRGGBB"} e.g. "FF0000"),
  format.size (params: {"size":18} = 18pt),
  format.highlight (params: {"color":"yellow"}),
  para.alignCenter, insert.table, insert.picture (params: {"path":"<TOOLS>\\images\\craft_test_banner.png"}),
  file.save (params: {"path":"<REPO>\\closed-qa\\craft-office-hard\\craft-hard-result.docx"})

Required content:
  1. Heading 1: "Project Aurora"
  2. Heading 2: "Quarterly Report"
  3. A paragraph with "Executive Summary"
  4. Somewhere the exact text "Q3 2026"
  5. BOLD text
  6. ITALIC text
  7. NON-BLACK colored text (e.g. FF0000)
  8. text at 16pt or larger (size:18 works)
  9. HIGHLIGHTED text
  10. a CENTER-aligned paragraph
  11. a TABLE
  12. the embedded image <TOOLS>\images\craft_test_banner.png

Important:
 - Put each piece of text in its own text.insert command with "paragraphs": true.
 - Apply a format command AFTER the text.insert that creates the text you want to
   format (select_text first if using the MCP path).
 - Run the batch, confirm the file was saved, then stop. Do not restart the document.
 - Report how many commands the batch contained and which path you used.

Actually execute it — do not just describe the script.
