#!/usr/bin/env Rscript

script_file <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[[1]])
script_dir <- dirname(normalizePath(script_file))
args <- commandArgs(trailingOnly = TRUE)

figures <- c(
  "graphical_abstract_v3.R",
  "fig1_dictionary.R",
  "fig2_janus.R",
  "fig3_curvature.R",
  "fig4_tilt.R",
  "fig5_data.R"
)

for (figure in figures) {
  message("Rendering ", figure)
  status <- system2("Rscript", c(file.path(script_dir, figure), args))
  if (status != 0L) stop("Render failed: ", figure)
}

