#!/usr/bin/env Rscript
# Build a local HTML reading copy from a Markdown master. Optional arguments:
#   render_html_mathjax.R INPUT.md OUTPUT.html
# MathJax is copied locally so browser-PDF export does not race a CDN load.
# The HTML reading copy is not arXiv source.

args <- commandArgs(trailingOnly = TRUE)
input <- if (length(args) >= 1L) args[[1L]] else "PAPER2_v2.md"
output <- if (length(args) >= 2L) args[[2L]] else sub("\\.md$", "_mathjax.html", input)

first_line <- readLines(input, n = 1L, warn = FALSE)
stopifnot(length(first_line) == 1L, grepl("^# ", first_line))
page_title <- sub("^# ", "", first_line)

rmarkdown::render(
  input,
  output_format = rmarkdown::html_document(
    self_contained = FALSE,
    mathjax = "local",
    css = "paper_pdf.css",
    pandoc_args = c(
      "-V", paste0("pagetitle=", page_title),
      "--lua-filter=math_glyphs.lua",
      "--lua-filter=vector_figures.lua",
      "--lua-filter=group_figures.lua"
    )
  ),
  output_file = output,
  quiet = TRUE
)
