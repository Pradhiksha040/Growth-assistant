import React, { useState } from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopyCode = (code: string, idx: number) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Helper to parse inline styles (bold, italic, inline code, links)
  const renderInline = (text: string): React.ReactNode[] => {
    const tokens: React.ReactNode[] = [];
    let remaining = text;
    let key = 0;

    // Pattern matches:
    // 1. `code`
    // 2. **bold**
    // 3. *italic*
    // 4. [label](url)
    const inlineRegex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/;

    while (remaining.length > 0) {
      const match = inlineRegex.exec(remaining);
      if (!match) {
        tokens.push(remaining);
        break;
      }

      if (match.index > 0) {
        tokens.push(remaining.substring(0, match.index));
      }

      const matchText = match[0];
      if (matchText.startsWith('`') && matchText.endsWith('`')) {
        tokens.push(
          <code key={key++} className="inline-code">
            {matchText.slice(1, -1)}
          </code>
        );
      } else if (matchText.startsWith('**') && matchText.endsWith('**')) {
        tokens.push(<strong key={key++}>{matchText.slice(2, -2)}</strong>);
      } else if (matchText.startsWith('*') && matchText.endsWith('*')) {
        tokens.push(<em key={key++}>{matchText.slice(1, -1)}</em>);
      } else if (matchText.startsWith('[') && matchText.includes('](')) {
        const endLabel = matchText.indexOf('](');
        const label = matchText.slice(1, endLabel);
        const url = matchText.slice(endLabel + 2, -1);
        tokens.push(
          <a
            key={key++}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="markdown-link"
          >
            {label}
          </a>
        );
      }

      remaining = remaining.substring(match.index + matchText.length);
    }

    return tokens;
  };

  // Parse blocks (paragraphs, headers, lists, code blocks, tables, blockquotes)
  const renderBlocks = () => {
    const lines = content.split('\n');
    const elements: React.ReactNode[] = [];
    let i = 0;
    let elementKey = 0;

    while (i < lines.length) {
      const line = lines[i];

      // 1. Code blocks
      if (line.trim().startsWith('```')) {
        const lang = line.trim().slice(3).trim() || 'plaintext';
        const codeLines: string[] = [];
        i++;
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeLines.push(lines[i]);
          i++;
        }
        i++; // skip closing ```
        const codeString = codeLines.join('\n');
        const codeIdx = elementKey;

        elements.push(
          <div key={elementKey++} className="code-block-wrapper">
            <div className="code-block-header">
              <span className="code-lang">{lang}</span>
              <button
                type="button"
                className="copy-code-btn"
                onClick={() => handleCopyCode(codeString, codeIdx)}
              >
                {copiedIndex === codeIdx ? '✓ Copied' : 'Copy'}
              </button>
            </div>
            <pre className="code-block">
              <code>{codeString}</code>
            </pre>
          </div>
        );
        continue;
      }

      // 2. Headings
      if (line.startsWith('# ')) {
        elements.push(<h1 key={elementKey++} className="md-h1">{renderInline(line.slice(2))}</h1>);
        i++;
        continue;
      }
      if (line.startsWith('## ')) {
        elements.push(<h2 key={elementKey++} className="md-h2">{renderInline(line.slice(3))}</h2>);
        i++;
        continue;
      }
      if (line.startsWith('### ')) {
        elements.push(<h3 key={elementKey++} className="md-h3">{renderInline(line.slice(4))}</h3>);
        i++;
        continue;
      }
      if (line.startsWith('#### ')) {
        elements.push(<h4 key={elementKey++} className="md-h4">{renderInline(line.slice(5))}</h4>);
        i++;
        continue;
      }

      // 3. Horizontal Rule
      if (line.trim() === '---' || line.trim() === '***') {
        elements.push(<hr key={elementKey++} className="md-hr" />);
        i++;
        continue;
      }

      // 4. Blockquotes
      if (line.startsWith('>')) {
        const quoteLines: string[] = [];
        while (i < lines.length && lines[i].startsWith('>')) {
          quoteLines.push(lines[i].replace(/^>\s?/, ''));
          i++;
        }
        elements.push(
          <blockquote key={elementKey++} className="md-blockquote">
            {quoteLines.map((ql, qIdx) => (
              <p key={qIdx}>{renderInline(ql)}</p>
            ))}
          </blockquote>
        );
        continue;
      }

      // 5. Unordered Lists (- or *)
      if (/^[-*]\s/.test(line.trim())) {
        const listItems: string[] = [];
        while (i < lines.length && /^[-*]\s/.test(lines[i].trim())) {
          listItems.push(lines[i].trim().replace(/^[-*]\s+/, ''));
          i++;
        }
        elements.push(
          <ul key={elementKey++} className="md-ul">
            {listItems.map((item, idx) => (
              <li key={idx}>{renderInline(item)}</li>
            ))}
          </ul>
        );
        continue;
      }

      // 6. Ordered Lists (1. 2.)
      if (/^\d+\.\s/.test(line.trim())) {
        const listItems: string[] = [];
        while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
          listItems.push(lines[i].trim().replace(/^\d+\.\s+/, ''));
          i++;
        }
        elements.push(
          <ol key={elementKey++} className="md-ol">
            {listItems.map((item, idx) => (
              <li key={idx}>{renderInline(item)}</li>
            ))}
          </ol>
        );
        continue;
      }

      // 7. Markdown Tables (| col | col |)
      if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
        const tableLines: string[] = [];
        while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
          tableLines.push(lines[i].trim());
          i++;
        }
        if (tableLines.length >= 2) {
          const headerCols = tableLines[0]
            .slice(1, -1)
            .split('|')
            .map((c) => c.trim());
          const bodyRows = tableLines.slice(2); // line 1 is separator |---|---|

          elements.push(
            <div key={elementKey++} className="md-table-wrapper">
              <table className="md-table">
                <thead>
                  <tr>
                    {headerCols.map((h, hIdx) => (
                      <th key={hIdx}>{renderInline(h)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {bodyRows.map((row, rIdx) => {
                    const cols = row
                      .slice(1, -1)
                      .split('|')
                      .map((c) => c.trim());
                    return (
                      <tr key={rIdx}>
                        {cols.map((col, cIdx) => (
                          <td key={cIdx}>{renderInline(col)}</td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // 8. Empty lines
      if (!line.trim()) {
        i++;
        continue;
      }

      // 9. Regular Paragraph
      elements.push(
        <p key={elementKey++} className="md-p">
          {renderInline(line)}
        </p>
      );
      i++;
    }

    return elements;
  };

  return <div className={`markdown-body ${className}`}>{renderBlocks()}</div>;
};
