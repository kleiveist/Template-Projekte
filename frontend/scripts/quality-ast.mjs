import fs from "node:fs";

import ts from "typescript";

const files = process.argv.slice(2);
const payload = { classes: [], imports: [] };

function lineNumber(source, position) {
  return source.getLineAndCharacterOfPosition(position).line + 1;
}

function stringArgument(node) {
  if (!node || (!ts.isStringLiteral(node) && !ts.isNoSubstitutionTemplateLiteral(node))) {
    return null;
  }
  return node.text;
}

function recordImport(source, file, specifierNode) {
  const specifier = stringArgument(specifierNode);
  if (specifier === null) return;
  payload.imports.push({
    file,
    line: lineNumber(source, specifierNode.getStart(source)),
    specifier
  });
}

function visit(source, file, node) {
  if (ts.isClassDeclaration(node) || ts.isClassExpression(node)) {
    payload.classes.push({
      file,
      line: lineNumber(source, node.getStart(source)),
      endLine: lineNumber(source, node.getEnd()),
      symbol: node.name?.text ?? "<anonymous class>"
    });
  }
  if (ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) {
    recordImport(source, file, node.moduleSpecifier);
  }
  if (ts.isCallExpression(node)) {
    const dynamicImport = node.expression.kind === ts.SyntaxKind.ImportKeyword;
    const commonJsRequire = ts.isIdentifier(node.expression) && node.expression.text === "require";
    if (dynamicImport || commonJsRequire) recordImport(source, file, node.arguments[0]);
  }
  ts.forEachChild(node, (child) => visit(source, file, child));
}

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const source = ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true);
  visit(source, file, source);
}

process.stdout.write(JSON.stringify(payload));
