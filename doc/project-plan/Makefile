# Makefile for LaTeX documents
#
# Intended for use in Linux and Git Bash
# TeXstudio (MiKTeX) compatibility through TeX directives
#
# by Dominik Mueller (@MuellerDominik)
#
# Targets:
#
# all						Build document if necessary
# build						Always (re)build document
# pdflatex					Run pdfLaTeX
# debug						Run pdfLaTeX in verbose mode
# bibliography, bib			Run biber
# glossary, makeglossaries	Run makeglossaries
# snapshot					Create snapshot
# remove-snapshots			Remove all snapshots
# directives				Add proper TeX directives
# remove-directives			Remove all TeX directives
# clean						Remove auxiliary files
# purge						Remove all generated files

# Document name
DOCUMENT = project-plan
OUTPUT = project-plan_aionfpga_canzani_mueller

# Directories and auxiliary files
TEMP_DIR = temp
BUILD_DIR = build
SECTIONS_DIR = sections
SNAPSHOTS_DIR = snapshots
PDF_FILE = $(BUILD_DIR)/$(OUTPUT).pdf
BIB_FILE = $(BUILD_DIR)/$(OUTPUT).bcf
GLOSS_FILE = $(BUILD_DIR)/$(OUTPUT).glo

# Source files (omit whitespaces) and timestamp
TEX_FILES := $(shell find . -name "*.tex")
TIMESTAMP := $(shell date +%Y-%m-%d_%H-%M-%S)

# Document ID (sliced for TeX directive 'document-id')
DOC_ID := $(shell echo -n $(TIMESTAMP) | sha256sum | cut -c1-32)
DOC_ID1 := $(shell echo -n $(DOC_ID) | cut -c1-8)
DOC_ID2 := $(shell echo -n $(DOC_ID) | cut -c9-12)
DOC_ID3 := $(shell echo -n $(DOC_ID) | cut -c13-16)
DOC_ID4 := $(shell echo -n $(DOC_ID) | cut -c17-20)
DOC_ID5 := $(shell echo -n $(DOC_ID) | cut -c21-32)

# Commands (with their respective arguments)
PDFLATEX_ARGS = -output-directory=$(BUILD_DIR) -jobname=$(OUTPUT) $(DOCUMENT)
PDFLATEX = pdflatex -interaction=batchmode $(PDFLATEX_ARGS) > /dev/null 2>&1
PDFLATEX_DEBUG = pdflatex -interaction=nonstopmode -halt-on-error $(PDFLATEX_ARGS)
BIBLIOGRAPHY = biber --onlylog --output-directory $(BUILD_DIR) $(OUTPUT)
GLOSSARY = makeglossaries -q -d $(BUILD_DIR) $(OUTPUT)

# TeX directives for TeXstudio with MiKTeX on Windows (Perl installed)
DIR_ID = % !TeX document-id = {$(DOC_ID1)-$(DOC_ID2)-$(DOC_ID3)-$(DOC_ID4)-$(DOC_ID5)}
DIR_COMPILE = % !TeX TXS-program:compile = pdflatex -synctex=1 -interaction=nonstopmode $(PDFLATEX_ARGS).tex
DIR_BIB = % !TeX TXS-program:bibliography = biber --output-directory $(BUILD_DIR) $(OUTPUT)
DIR_GLOSS = % !TeX TXS-program:glossary = makeglossaries -d $(BUILD_DIR) $(OUTPUT)
DIR_VIEW = % !TeX TXS-program:view = txs:///view-pdf ./$(BUILD_DIR)/$(OUTPUT).pdf
DIRECTIVES = $(DIR_ID)\n$(DIR_COMPILE)\n$(DIR_BIB)\n$(DIR_GLOSS)\n$(DIR_VIEW)\n\n

# Rebuilds document if source files (*.tex only) have been changed
.PHONY: all
all: $(PDF_FILE)

.PHONY: build
build $(PDF_FILE): $(TEX_FILES)
	@mkdir -p $(BUILD_DIR)/$(SECTIONS_DIR)/
	@$(PDFLATEX)
	@$(BIBLIOGRAPHY)
	@$(GLOSSARY)
	@$(PDFLATEX)
	@$(PDFLATEX)

.PHONY: pdflatex
pdflatex $(BIB_FILE) $(GLOSS_FILE):
	@$(PDFLATEX)

.PHONY: debug
debug:
	@$(PDFLATEX_DEBUG)

.PHONY: bibliography bib
bibliography bib: $(BIB_FILE)
	@$(BIBLIOGRAPHY)

.PHONY: glossary makeglossaries
glossary makeglossaries: $(GLOSS_FILE)
	@$(GLOSSARY)

.PHONY: snapshot
snapshot:
	@mkdir -p $(SNAPSHOTS_DIR)/
	@cp -f $(PDF_FILE) $(SNAPSHOTS_DIR)/$(OUTPUT)_$(TIMESTAMP).pdf

.PHONY: remove-snapshots
remove-snapshots:
	@rm -rf $(SNAPSHOTS_DIR)/

# Removes all TeX directives and prepends the ones specified in this Makefile
.PHONY: directives
directives:
	@sed -i '/^% !TeX/d' $(DOCUMENT).tex
	@sed -i '/./,$$!d' $(DOCUMENT).tex
	@sed -i '1s;^;$(DIRECTIVES);' $(DOCUMENT).tex

# Removes all TeX directives and leading blank lines
.PHONY: remove-directives
remove-directives:
	@sed -i '/^% !TeX/d' $(DOCUMENT).tex
	@sed -i '/./,$$!d' $(DOCUMENT).tex

.PHONY: clean
clean:
	@mkdir -p $(TEMP_DIR)/
	@cp -f $(PDF_FILE) $(TEMP_DIR)/$(OUTPUT).pdf > /dev/null 2>&1 || :
	@rm -rf $(BUILD_DIR)/* > /dev/null 2>&1 || :
	@cp -f $(TEMP_DIR)/$(OUTPUT).pdf $(PDF_FILE) > /dev/null 2>&1 || :
	@rm -rf $(TEMP_DIR)/

.PHONY: purge
purge:
	@rm -rf $(BUILD_DIR)/ $(TEMP_DIR)/
