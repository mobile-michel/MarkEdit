package li.maillard.markedit

import org.commonmark.ext.gfm.strikethrough.StrikethroughExtension
import org.commonmark.ext.gfm.tables.TablesExtension
import org.commonmark.ext.heading.anchor.HeadingAnchorExtension
import org.commonmark.ext.heading.anchor.IdGenerator
import org.commonmark.node.AbstractVisitor
import org.commonmark.node.Code
import org.commonmark.node.Heading
import org.commonmark.node.Node
import org.commonmark.node.Text
import org.commonmark.parser.Parser
import org.commonmark.renderer.html.HtmlRenderer

/** Une entrée du sommaire : niveau de titre (1..6), texte et ancre HTML. */
data class TocItem(val level: Int, val title: String, val anchor: String)

/**
 * Conversion Markdown -> HTML, équivalent Android du rendu de `markdown_app.py`.
 * Les feuilles de style reprennent les thèmes « Classique » et « Sombre » du
 * bureau, retaillés pour un écran de téléphone : marges réduites et pas de
 * largeur de colonne fixe.
 *
 * Le thème sombre est piloté par un drapeau plutôt que par la media query
 * `prefers-color-scheme` : sur Android, c'est déterministe et indépendant du
 * comportement d'auto-assombrissement de la WebView.
 */
object MarkdownRenderer {

    private val extensions = listOf(
        TablesExtension.create(),
        StrikethroughExtension.create(),
        HeadingAnchorExtension.create(),
    )
    private val parser: Parser = Parser.builder().extensions(extensions).build()
    private val renderer: HtmlRenderer =
        HtmlRenderer.builder().extensions(extensions).build()

    private const val LIGHT_CSS = """
body { font-family:"Noto Sans",system-ui,sans-serif; font-size:16px; line-height:1.7;
       color:#1a1a1a; background:#fff; margin:0; padding:16px 18px; }
h1,h2,h3,h4,h5,h6 { margin-top:1.4em; margin-bottom:0.6em; font-weight:600; line-height:1.3; color:#111; }
h1 { font-size:1.8em; border-bottom:2px solid #e0e0e0; padding-bottom:0.3em; }
h2 { font-size:1.4em; border-bottom:1px solid #e8e8e8; padding-bottom:0.25em; }
h3 { font-size:1.2em; } h4 { font-size:1.05em; }
p { margin:0.8em 0; }
a { color:#0366d6; text-decoration:none; }
ul,ol { padding-left:1.5em; margin:0.6em 0; } li { margin:0.25em 0; }
table { border-collapse:collapse; width:100%; }
th,td { border:1px solid #d0d0d0; padding:8px 12px; text-align:left;
        word-wrap:break-word; overflow-wrap:break-word; }
th { background:#f0f0f0; font-weight:600; }
tr:nth-child(even) { background:#fafafa; }
code { font-family:"Fira Code",monospace; font-size:0.9em;
       background:#f4f4f4; padding:2px 6px; border-radius:3px; }
pre { background:#f6f8fa; padding:12px; border-radius:6px; overflow-x:auto;
      line-height:1.5; border:1px solid #e1e4e8; }
pre code { background:none; padding:0; font-size:0.88em; }
blockquote { border-left:4px solid #3b82f6; margin:1em 0; padding:0.5em 1em;
             background:#eff6ff; color:#333; }
blockquote p { margin:0.4em 0; }
hr { border:none; border-top:2px solid #e0e0e0; margin:2em 0; }
img { max-width:100%; height:auto; }
del { color:#777; }
"""

    private const val DARK_CSS = """
body { font-family:"Noto Sans",system-ui,sans-serif; font-size:16px; line-height:1.7;
       color:#cdd6f4; background:#1e1e2e; margin:0; padding:16px 18px; }
h1,h2,h3,h4,h5,h6 { margin-top:1.4em; margin-bottom:0.6em; font-weight:600; line-height:1.3; color:#e6edf3; }
h1 { font-size:1.8em; border-bottom:2px solid #313244; padding-bottom:0.3em; }
h2 { font-size:1.4em; border-bottom:1px solid #313244; padding-bottom:0.25em; }
h3 { font-size:1.2em; } h4 { font-size:1.05em; }
p { margin:0.8em 0; }
a { color:#89b4fa; text-decoration:none; }
ul,ol { padding-left:1.5em; margin:0.6em 0; } li { margin:0.25em 0; }
table { border-collapse:collapse; width:100%; }
th,td { border:1px solid #45475a; padding:8px 12px; text-align:left;
        word-wrap:break-word; overflow-wrap:break-word; }
th { background:#313244; font-weight:600; }
tr:nth-child(even) { background:#181825; }
code { font-family:"Fira Code",monospace; font-size:0.9em;
       background:#313244; color:#f38ba8; padding:2px 6px; border-radius:3px; }
pre { background:#181825; padding:12px; border-radius:6px; overflow-x:auto;
      line-height:1.5; border:1px solid #313244; }
pre code { background:none; padding:0; font-size:0.88em; color:inherit; }
blockquote { border-left:4px solid #89b4fa; margin:1em 0; padding:0.5em 1em;
             background:#181825; color:#a6adc8; }
blockquote p { margin:0.4em 0; }
hr { border:none; border-top:2px solid #313244; margin:2em 0; }
img { max-width:100%; height:auto; }
del { color:#9198a1; }
"""

    /** Produit un document HTML complet à charger dans une WebView. */
    fun toHtml(markdown: String, dark: Boolean): String {
        val body = renderer.render(parser.parse(markdown))
        val css = if (dark) DARK_CSS else LIGHT_CSS
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>$css</style>
            </head>
            <body>$body</body>
            </html>
        """.trimIndent()
    }

    /**
     * Sommaire (titres dans l'ordre du document), avec l'ancre générée par
     * `HeadingAnchorExtension` — la même que celle posée sur les `<h1..h6>` du
     * HTML rendu, ce qui permet d'y faire défiler par `getElementById`.
     */
    fun tableOfContents(markdown: String): List<TocItem> {
        val items = mutableListOf<TocItem>()
        val ids = IdGenerator.builder().build()
        parser.parse(markdown).accept(object : AbstractVisitor() {
            override fun visit(heading: Heading) {
                val title = textOf(heading)
                items.add(TocItem(heading.level, title, ids.generateId(title)))
            }
        })
        return items
    }

    /** Concatène le texte brut contenu dans un nœud (titre). */
    private fun textOf(node: Node): String {
        val sb = StringBuilder()
        node.accept(object : AbstractVisitor() {
            override fun visit(text: Text) { sb.append(text.literal) }
            override fun visit(code: Code) { sb.append(code.literal) }
        })
        return sb.toString().trim()
    }
}
