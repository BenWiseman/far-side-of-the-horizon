#!/usr/bin/env Rscript

# Audit SVG text sizes at final journal reproduction width.
# Usage: Rscript audit_svg_legibility_v3.R [width_inches] file1.svg ...

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L) {
  stop("usage: audit_svg_legibility_v3.R width_inches file1.svg [file2.svg ...]")
}

final_width_in <- as.numeric(args[[1]])
if (!is.finite(final_width_in) || final_width_in <= 0) stop("width_inches must be positive")
files <- args[-1]

extract_one <- function(path) {
  x <- paste(readLines(path, warn = FALSE), collapse = "\n")
  vb <- regexec('viewBox="[[:space:]]*[-0-9.]+[[:space:]]+[-0-9.]+[[:space:]]+([0-9.]+)[[:space:]]+([0-9.]+)"', x)
  hit <- regmatches(x, vb)[[1]]
  if (length(hit) != 3L) stop("missing or malformed viewBox: ", path)
  vb_width <- as.numeric(hit[[2]])

  pats <- c(
    'font-size="([0-9.]+)(?:pt|px)?"',
    "font-size='([0-9.]+)(?:pt|px)?'",
    'font-size:[[:space:]]*([0-9.]+)px',
    'font-size:[[:space:]]*([0-9.]+)'
  )
  vals <- numeric()
  for (pat in pats) {
    m <- gregexpr(pat, x, perl = TRUE)
    hits <- regmatches(x, m)[[1]]
    if (length(hits) && hits[[1]] != "") {
      vals <- c(vals, as.numeric(sub(pat, "\\1", hits, perl = TRUE)))
    }
  }
  vals <- unique(vals[is.finite(vals)])
  if (!length(vals)) stop("no numeric font sizes found: ", path)
  pts <- vals * final_width_in * 72 / vb_width
  data.frame(
    file = basename(path),
    viewbox_width = vb_width,
    source_min = min(vals),
    final_min_pt = min(pts),
    final_median_pt = median(pts),
    final_max_pt = max(pts),
    stringsAsFactors = FALSE
  )
}

out <- do.call(rbind, lapply(files, extract_one))
print(out, row.names = FALSE, digits = 3)

# Eight points is the absolute floor. Axes, annotations and legends should be >=9 pt;
# this mechanical gate cannot distinguish an essential label from secondary furniture.
if (any(out$final_min_pt < 8)) {
  stop("FAIL: at least one SVG contains text below the 8 pt absolute floor at final width")
}

cat("PASS: no SVG text below 8 pt at", final_width_in, "inch width\n")
