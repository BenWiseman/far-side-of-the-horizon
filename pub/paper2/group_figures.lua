-- Group each Appendix C image with the following detailed caption in a single
-- Pandoc Figure, so LaTeX does not strand captions on a different page.
function Pandoc(doc)
  local alt_text = {
    ["1"] = "Five CPT fold positions compared by fixed set, price and verdict",
    ["2"] = "Two plots of Bel-Robinson complexity near the bang for regular and irregular modes",
    ["3"] = "Discrete curvature values compared with Planck and DESI constraints",
    ["4"] = "Primordial tilt prediction compared with eight published estimates and error bars",
    ["5"] = "Neutrino-mass bounds and dark-energy fits compared with the framework's prediction",
  }
  local grouped = pandoc.List()
  local i = 1
  while i <= #doc.blocks do
    local image_block = doc.blocks[i]
    local caption_block = doc.blocks[i + 1]
    local image = image_block and image_block.t == "Para" and
      #image_block.content == 1 and image_block.content[1].t == "Image" and
      image_block.content[1] or nil
    local number = image and image.src:match("^fig([1-5])_") or nil
    local heading = caption_block and caption_block.t == "Para" and
      caption_block.content[1] and caption_block.content[1].t == "Strong" and
      caption_block.content[1] or nil
    local caption_number = heading and heading.content[3] and heading.content[3].text and
      heading.content[3].text:match("^(%d+):$") or nil
    if number and heading and heading.content[1] and heading.content[1].text == "Figure" and
        caption_number == number then
      local title = pandoc.List()
      for k = 5, #heading.content do title:insert(heading.content[k]) end
      image.caption = {pandoc.Str(alt_text[number])}
      -- Figure 5 has a deliberately detailed evidentiary caption.  At full
      -- line width the vector image plus caption exceeds a letter-size text
      -- block.  This LaTeX-only scale keeps the smallest 10 pt figure label
      -- just above 8 pt in the submitted PDF and keeps the complete float on
      -- one page.  HTML continues to use the full-width responsive image.
      if number == "5" and FORMAT:match("latex") then
        image.attributes["width"] = "86.5%"
      end
      local inlines = pandoc.List({pandoc.Strong(title)})
      for k = 2, #caption_block.content do inlines:insert(caption_block.content[k]) end
      local caption = {long = {pandoc.Para(inlines)}, short = {}}
      if number == "5" then
        grouped:insert(pandoc.RawBlock("latex", "\\clearpage\n\\captionsetup{font=paper2compact}\n\\setcounter{figure}{4}"))
      end
      grouped:insert(pandoc.Figure({image_block}, caption, pandoc.Attr("fig" .. number)))
      if number == "5" then
        grouped:insert(pandoc.RawBlock("latex", "\\clearpage"))
      end
      i = i + 2
    else
      if image_block.t == "Header" and
          (pandoc.utils.stringify(image_block.content) == "Acknowledgements" or
           pandoc.utils.stringify(image_block.content):match("^S13%.")) then
        grouped:insert(pandoc.RawBlock("latex", "\\clearpage"))
      end
      grouped:insert(image_block)
      i = i + 1
    end
  end
  doc.blocks = grouped
  return doc
end
