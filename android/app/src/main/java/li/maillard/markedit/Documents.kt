package li.maillard.markedit

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.DocumentsContract
import androidx.activity.result.contract.ActivityResultContracts
import androidx.documentfile.provider.DocumentFile

/** Extensions considérées comme du Markdown, comme côté bureau. */
val MARKDOWN_SUFFIXES = listOf(".md", ".markdown", ".mkd")

fun String.isMarkdownName(): Boolean =
    MARKDOWN_SUFFIXES.any { lowercase().endsWith(it) }

/**
 * Document ouvert. `parent` n'est connu que si le fichier a été atteint via un
 * dossier autorisé (Storage Access Framework, `ACTION_OPEN_DOCUMENT_TREE`) :
 * c'est ce qui permet de résoudre les liens Markdown relatifs. Un fichier
 * ouvert seul reste lisible et modifiable, mais sans navigation entre fichiers.
 */
data class OpenDoc(
    val uri: Uri,
    val name: String,
    val parent: DocumentFile? = null,
)

/** Nombre de champs produits par [OpenDoc.toFields] — voir les savers d'état. */
const val FIELDS_PER_DOC = 3

/** Sérialise un document pour la sauvegarde d'état (rotation, recréation). */
fun OpenDoc.toFields(): List<String> =
    listOf(uri.toString(), name, parent?.uri?.toString().orEmpty())

/** Inverse de [OpenDoc.toFields] ; null si les champs sont inexploitables. */
fun List<String>.toOpenDoc(context: Context): OpenDoc? {
    if (size < FIELDS_PER_DOC || this[0].isEmpty()) return null
    val parent = this[2].takeIf { it.isNotEmpty() }
        ?.let { treeDocument(context, Uri.parse(it)) }
    return OpenDoc(Uri.parse(this[0]), this[1], parent)
}

/**
 * Contrat d'ouverture : comme `OpenDocument`, mais en demandant aussi l'accès
 * en écriture et la persistance de l'autorisation — sans quoi « Enregistrer »
 * échouerait, et l'autorisation serait perdue au redémarrage.
 */
class OpenWritableDocument : ActivityResultContracts.OpenDocument() {
    override fun createIntent(context: Context, input: Array<String>): Intent =
        super.createIntent(context, input).apply {
            addFlags(
                Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
                    Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION,
            )
        }
}

/**
 * Dossier désigné par [uri], ou null si ce n'en est pas un.
 *
 * `DocumentFile.fromTreeUri` lève une exception — au lieu de renvoyer null —
 * sur une URI de document simple, ce qu'on trouve parmi les autorisations
 * persistées dès qu'un fichier a été ouvert seul.
 */
fun treeDocument(context: Context, uri: Uri): DocumentFile? = runCatching {
    if (DocumentsContract.isTreeUri(uri)) DocumentFile.fromTreeUri(context, uri) else null
}.getOrNull()

object Documents {

    val MIME_TYPES = arrayOf("text/markdown", "text/plain", "text/*")

    fun readText(context: Context, uri: Uri): Result<String> = runCatching {
        context.contentResolver.openInputStream(uri)?.use { it.bufferedReader().readText() }
            ?: error("flux d'entrée indisponible")
    }

    fun writeText(context: Context, uri: Uri, text: String): Result<Unit> = runCatching {
        // "wt" tronque le fichier existant : sans ça, un document plus court
        // laisserait la fin de l'ancien contenu derrière lui.
        context.contentResolver.openOutputStream(uri, "wt")?.use {
            it.write(text.toByteArray(Charsets.UTF_8))
        } ?: error("flux de sortie indisponible")
    }

    fun displayName(context: Context, uri: Uri): String =
        DocumentFile.fromSingleUri(context, uri)?.name
            ?: uri.lastPathSegment?.substringAfterLast('/')
            ?: "Document"

    /** Conserve l'autorisation au-delà de la session en cours. */
    fun persist(context: Context, uri: Uri, writable: Boolean) {
        val flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or
            if (writable) Intent.FLAG_GRANT_WRITE_URI_PERMISSION else 0
        runCatching { context.contentResolver.takePersistableUriPermission(uri, flags) }
    }

    /** Fichiers Markdown d'un dossier, triés par nom. */
    fun listMarkdown(dir: DocumentFile): List<DocumentFile> =
        dir.listFiles()
            .filter { it.isFile && (it.name?.isMarkdownName() == true) }
            .sortedBy { it.name?.lowercase() }

    /**
     * Résout la cible d'un lien Markdown relatif (« page2.md »,
     * « ../notes/index.md ») à partir du dossier du document courant.
     * Renvoie null si le dossier n'est pas connu ou si le fichier est absent.
     */
    fun resolveRelative(parent: DocumentFile?, relativePath: String): DocumentFile? {
        var dir = parent ?: return null
        val segments = relativePath.trim('/').split('/').filter { it.isNotEmpty() }
        if (segments.isEmpty()) return null
        for (segment in segments.dropLast(1)) {
            dir = when (segment) {
                "." -> dir
                ".." -> dir.parentFile ?: return null
                else -> dir.findFile(segment)?.takeIf { it.isDirectory } ?: return null
            }
        }
        return dir.findFile(segments.last())?.takeIf { it.isFile }
    }
}
