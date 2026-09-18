-- Route every rendered manuscript to a vector asset. XeLaTeX uses PDF;
-- browser/MathJax output uses SVG so zooming and printing stay crisp.
function Image(el)
  local extension = FORMAT:match("html") and ".svg" or ".pdf"
  if el.src:match("^fig[1-5]_[%w_]+%.png$") then
    el.src = el.src:gsub("%.png$", extension)
  elseif el.src == "graphical_abstract_v3.png" then
    el.src = "graphical_abstract_v3" .. extension
  end
  return el
end
