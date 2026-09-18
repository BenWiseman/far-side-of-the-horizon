-- Convert mathematical Unicode glyphs not supplied by the document's text font
-- into ordinary LaTeX math commands. This keeps the source portable for arXiv.
local symbols = {
  {"𝒫", "\\mathcal{P}"},
  {"𝒜", "\\mathcal{A}"},
  {"𝒩", "\\mathcal{N}"},
  {"ℋ", "\\mathcal{H}"},
  {"ℓ", "\\ell"},
  {"≳", "\\gtrsim"},
  {"≲", "\\lesssim"},
  {"≪", "\\ll"},
}

function Str(el)
  local source = el.text
  local result = pandoc.List()
  local cursor = 1
  while cursor <= #source do
    local first, last, command
    for _, item in ipairs(symbols) do
      local start_at, end_at = source:find(item[1], cursor, true)
      if start_at and (not first or start_at < first) then
        first, last, command = start_at, end_at, item[2]
      end
    end
    if not first then
      if cursor == 1 then return nil end
      result:insert(pandoc.Str(source:sub(cursor)))
      break
    end
    if first > cursor then result:insert(pandoc.Str(source:sub(cursor, first - 1))) end
    result:insert(pandoc.Math("InlineMath", command))
    cursor = last + 1
  end
  return result
end
