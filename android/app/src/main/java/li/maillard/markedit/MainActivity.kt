package li.maillard.markedit

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.MotionEvent
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.listSaver
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.documentfile.provider.DocumentFile
import kotlinx.coroutines.launch

/**
 * Base des pages rendues. Les liens relatifs du document deviennent des URL
 * sous cette base, ce qui les rend interceptables ; les ancres « #… » gardent
 * cette base et restent traitées par la WebView elle-même.
 */
private const val BASE_URL = "file:///android_asset/"

private const val PLACEHOLDER = """# MarkEdit

Ouvrez un fichier ou un dossier depuis le menu **⋮**, ou commencez à écrire
dans l'onglet **Édition**.
"""

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fichier éventuellement transmis via une intent VIEW / EDIT.
        val initialUri: Uri? = intent?.data
        setContent {
            val colors = if (isSystemInDarkTheme()) darkColorScheme() else lightColorScheme()
            MaterialTheme(colorScheme = colors) {
                EditorScreen(initialUri)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@SuppressLint("ClickableViewAccessibility")   // la WebView gère elle-même ses clics
@Composable
fun EditorScreen(initialUri: Uri?) {
    val context = LocalContext.current
    val dark = isSystemInDarkTheme()
    val scope = rememberCoroutineScope()
    val snackbar = remember { SnackbarHostState() }
    val drawerState = rememberDrawerState(DrawerValue.Closed)

    // L'activité est recréée à chaque rotation, changement de thème système ou
    // retour d'un sélecteur : sans rememberSaveable, le document ouvert et les
    // modifications en cours seraient perdus à chaque fois.
    val docSaver = remember(context) {
        listSaver<OpenDoc?, String>(
            save = { doc -> if (doc == null) emptyList() else doc.toFields() },
            restore = { fields -> fields.toOpenDoc(context) },
        )
    }
    val historySaver = remember(context) {
        listSaver<MutableList<OpenDoc>, String>(
            save = { list -> list.flatMap { it.toFields() } },
            restore = { flat ->
                mutableStateListOf<OpenDoc>().apply {
                    flat.chunked(FIELDS_PER_DOC).forEach { fields ->
                        fields.toOpenDoc(context)?.let { add(it) }
                    }
                }
            },
        )
    }

    var text by rememberSaveable { mutableStateOf(PLACEHOLDER) }
    var savedText by rememberSaveable { mutableStateOf(PLACEHOLDER) }
    var current by rememberSaveable(stateSaver = docSaver) { mutableStateOf<OpenDoc?>(null) }
    var folderUri by rememberSaveable { mutableStateOf<String?>(null) }
    val history = rememberSaveable(saver = historySaver) { mutableStateListOf<OpenDoc>() }
    val folder = remember(folderUri) {
        folderUri?.let { treeDocument(context, Uri.parse(it)) }
    }

    var toc by remember { mutableStateOf(MarkdownRenderer.tableOfContents(PLACEHOLDER)) }
    var tab by rememberSaveable { mutableIntStateOf(0) }
    var previewSource by remember { mutableStateOf(PLACEHOLDER) }
    var menuExpanded by remember { mutableStateOf(false) }
    var searchVisible by rememberSaveable { mutableStateOf(false) }
    var searchQuery by rememberSaveable { mutableStateOf("") }
    var webView by remember { mutableStateOf<WebView?>(null) }
    var showFolderPicker by rememberSaveable { mutableStateOf(false) }
    var pendingAction by remember { mutableStateOf<(() -> Unit)?>(null) }
    val pendingAnchor = remember { mutableStateOf<String?>(null) }

    // Le sommaire et l'aperçu se redéduisent du texte restauré.
    LaunchedEffect(Unit) {
        if (text != PLACEHOLDER) {
            toc = MarkdownRenderer.tableOfContents(text)
            previewSource = text
        }
    }

    val modified = text != savedText
    val title = (current?.name ?: "Sans titre") + if (modified) " •" else ""

    fun say(message: String) {
        scope.launch { snackbar.showSnackbar(message) }
    }

    fun load(doc: OpenDoc, anchor: String? = null, push: Boolean = true) {
        Documents.readText(context, doc.uri)
            .onSuccess { content ->
                if (push) current?.let { history.add(it) }
                current = doc
                text = content
                savedText = content
                toc = MarkdownRenderer.tableOfContents(content)
                previewSource = content
                pendingAnchor.value = anchor
                tab = 0
            }
            .onFailure { say("Impossible d'ouvrir « ${doc.name} ».") }
    }

    /** Exécute l'action, en proposant d'abord d'enregistrer si nécessaire. */
    fun guard(action: () -> Unit) {
        if (modified) pendingAction = action else action()
    }

    val opener = rememberLauncherForActivityResult(OpenWritableDocument()) { uri ->
        if (uri != null) {
            Documents.persist(context, uri, writable = true)
            load(OpenDoc(uri, Documents.displayName(context, uri)))
        }
    }

    val folderOpener = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocumentTree(),
    ) { uri ->
        if (uri != null) {
            Documents.persist(context, uri, writable = true)
            folderUri = uri.toString()
            showFolderPicker = true
        }
    }

    val creator = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("text/markdown"),
    ) { uri ->
        if (uri != null) {
            Documents.persist(context, uri, writable = true)
            Documents.writeText(context, uri, text)
                .onSuccess {
                    current = OpenDoc(uri, Documents.displayName(context, uri))
                    savedText = text
                    say("Enregistré : ${current?.name}")
                }
                .onFailure { say("Échec de l'enregistrement.") }
        }
    }

    val exporter = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("text/html"),
    ) { uri ->
        if (uri != null) {
            Documents.writeText(context, uri, MarkdownRenderer.toHtml(text, dark))
                .onSuccess { say("Exporté en HTML.") }
                .onFailure { say("Échec de l'export.") }
        }
    }

    fun save() {
        val doc = current
        if (doc == null) {
            creator.launch("document.md")
            return
        }
        Documents.writeText(context, doc.uri, text)
            .onSuccess {
                savedText = text
                say("Enregistré : ${doc.name}")
            }
            .onFailure { say("Échec de l'enregistrement — essayez « Enregistrer sous ».") }
    }

    fun goBack() {
        while (history.isNotEmpty()) {
            val previous = history.removeAt(history.size - 1)
            guard { load(previous, push = false) }
            return
        }
    }

    /** Aiguillage d'un lien cliqué dans l'aperçu. */
    fun handleLink(uri: Uri): Boolean {
        val url = uri.toString()
        if (url.startsWith(BASE_URL)) {
            val rest = url.removePrefix(BASE_URL)
            val path = Uri.decode(rest.substringBefore('#'))
            val anchor = rest.substringAfter('#', "").ifEmpty { null }
            // Ancre du document courant : la WebView s'en charge.
            if (path.isEmpty()) return false
            if (path.isMarkdownName()) {
                val target = Documents.resolveRelative(current?.parent, path)
                if (target == null) {
                    say("Ouvrez le dossier (menu ⋮) pour suivre les liens entre fichiers.")
                } else {
                    guard {
                        load(
                            OpenDoc(target.uri, target.name ?: path, target.parentFile),
                            anchor = anchor,
                        )
                    }
                }
                return true
            }
        }
        runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, uri)) }
            .onFailure { say("Aucune application ne peut ouvrir ce lien.") }
        return true
    }

    val onLink by rememberUpdatedState(::handleLink)

    LaunchedEffect(initialUri) {
        if (initialUri != null) {
            Documents.persist(context, initialUri, writable = true)
            load(OpenDoc(initialUri, Documents.displayName(context, initialUri)))
        }
        // Dossier déjà autorisé lors d'une session précédente.
        if (folderUri == null) {
            context.contentResolver.persistedUriPermissions
                .firstOrNull {
                    it.isReadPermission &&
                        treeDocument(context, it.uri)?.isDirectory == true
                }
                ?.let { folderUri = it.uri.toString() }
        }
    }

    // L'aperçu se resynchronise en entrant dans l'onglet, pas à chaque frappe.
    LaunchedEffect(tab, text) {
        if (tab == 0) previewSource = text
    }

    LaunchedEffect(searchQuery, searchVisible) {
        if (searchVisible && searchQuery.isNotEmpty()) webView?.findAllAsync(searchQuery)
        else webView?.clearMatches()
    }

    val html = remember(previewSource, dark) { MarkdownRenderer.toHtml(previewSource, dark) }

    BackHandler(enabled = history.isNotEmpty()) { goBack() }

    if (pendingAction != null) {
        AlertDialog(
            onDismissRequest = { pendingAction = null },
            title = { Text("Modifications non enregistrées") },
            text = { Text("Le document « ${current?.name ?: "Sans titre"} » a été modifié.") },
            confirmButton = {
                TextButton(onClick = {
                    val action = pendingAction
                    pendingAction = null
                    save()
                    action?.invoke()
                }) { Text("Enregistrer") }
            },
            dismissButton = {
                Row {
                    TextButton(onClick = { pendingAction = null }) { Text("Annuler") }
                    TextButton(onClick = {
                        val action = pendingAction
                        pendingAction = null
                        savedText = text          // abandonne les modifications
                        action?.invoke()
                    }) { Text("Ne pas enregistrer") }
                }
            },
        )
    }

    if (showFolderPicker) {
        val files = remember(folder) { folder?.let { Documents.listMarkdown(it) } ?: emptyList() }
        AlertDialog(
            onDismissRequest = { showFolderPicker = false },
            title = { Text(folder?.name ?: "Dossier") },
            text = {
                if (files.isEmpty()) {
                    Text("Aucun fichier Markdown dans ce dossier.")
                } else {
                    Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                        files.forEach { file ->
                            TextButton(onClick = {
                                showFolderPicker = false
                                guard {
                                    load(OpenDoc(file.uri, file.name ?: "Document", file.parentFile))
                                }
                            }) { Text(file.name ?: "?") }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showFolderPicker = false }) { Text("Fermer") }
            },
        )
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Text(
                    "Sommaire",
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.titleLarge,
                )
                if (toc.isEmpty()) Text("Aucun titre", modifier = Modifier.padding(16.dp))
                Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                    toc.forEach { item ->
                        NavigationDrawerItem(
                            label = {
                                Text(
                                    item.title,
                                    maxLines = 1,
                                    modifier = Modifier.padding(start = ((item.level - 1) * 12).dp),
                                )
                            },
                            selected = false,
                            onClick = {
                                tab = 0
                                webView?.evaluateJavascript(
                                    "var el = document.getElementById('${item.anchor}');" +
                                        "if (el) el.scrollIntoView({behavior:'smooth', block:'start'});",
                                    null,
                                )
                                scope.launch { drawerState.close() }
                            },
                        )
                    }
                }
            }
        },
    ) {
        Scaffold(
            snackbarHost = { SnackbarHost(snackbar) },
            topBar = {
                TopAppBar(
                    title = { Text(title, maxLines = 1) },
                    navigationIcon = {
                        IconButton(onClick = { scope.launch { drawerState.open() } }) {
                            Icon(Icons.Filled.Menu, contentDescription = "Sommaire")
                        }
                    },
                    actions = {
                        if (history.isNotEmpty()) {
                            IconButton(onClick = { goBack() }) {
                                Icon(
                                    Icons.AutoMirrored.Filled.ArrowBack,
                                    contentDescription = "Précédent",
                                )
                            }
                        }
                        IconButton(onClick = {
                            searchVisible = !searchVisible
                            if (searchVisible) tab = 0 else searchQuery = ""
                        }) {
                            Icon(Icons.Filled.Search, contentDescription = "Rechercher")
                        }
                        IconButton(onClick = { menuExpanded = true }) {
                            Icon(Icons.Filled.MoreVert, contentDescription = "Plus")
                        }
                        DropdownMenu(
                            expanded = menuExpanded,
                            onDismissRequest = { menuExpanded = false },
                        ) {
                            DropdownMenuItem(
                                text = { Text("Nouveau") },
                                onClick = {
                                    menuExpanded = false
                                    guard {
                                        current?.let { history.add(it) }
                                        current = null
                                        text = ""
                                        savedText = ""
                                        toc = emptyList()
                                        previewSource = ""
                                        tab = 1
                                    }
                                },
                            )
                            DropdownMenuItem(
                                text = { Text("Ouvrir un fichier…") },
                                onClick = {
                                    menuExpanded = false
                                    guard { opener.launch(Documents.MIME_TYPES) }
                                },
                            )
                            DropdownMenuItem(
                                text = { Text("Ouvrir un dossier…") },
                                onClick = {
                                    menuExpanded = false
                                    folderOpener.launch(null)
                                },
                            )
                            if (folder != null) {
                                DropdownMenuItem(
                                    text = { Text("Fichiers du dossier…") },
                                    onClick = {
                                        menuExpanded = false
                                        showFolderPicker = true
                                    },
                                )
                            }
                            DropdownMenuItem(
                                text = { Text("Enregistrer") },
                                onClick = {
                                    menuExpanded = false
                                    save()
                                },
                            )
                            DropdownMenuItem(
                                text = { Text("Enregistrer sous…") },
                                onClick = {
                                    menuExpanded = false
                                    creator.launch(current?.name ?: "document.md")
                                },
                            )
                            DropdownMenuItem(
                                text = { Text("Exporter en HTML…") },
                                onClick = {
                                    menuExpanded = false
                                    val base = (current?.name ?: "document")
                                        .substringBeforeLast('.')
                                    exporter.launch("$base.html")
                                },
                            )
                        }
                    },
                )
            },
        ) { innerPadding ->
            Column(modifier = Modifier.padding(innerPadding).fillMaxSize()) {
                if (searchVisible) {
                    SearchRow(
                        query = searchQuery,
                        onQueryChange = { searchQuery = it },
                        onPrevious = { webView?.findNext(false) },
                        onNext = { webView?.findNext(true) },
                        onClose = {
                            searchVisible = false
                            searchQuery = ""
                            webView?.clearMatches()
                        },
                    )
                }

                TabRow(selectedTabIndex = tab) {
                    Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("Aperçu") })
                    Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("Édition") })
                }

                Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
                    // La WebView reste composée (préserve défilement et
                    // recherche) ; l'éditeur la recouvre quand il est actif.
                    AndroidView(
                        modifier = Modifier.fillMaxSize(),
                        factory = { ctx ->
                            WebView(ctx).apply {
                                settings.javaScriptEnabled = true
                                overScrollMode = WebView.OVER_SCROLL_NEVER
                                // Sans ça, Compose s'approprie le geste vertical
                                // dès les premiers pixels et le défilement de la
                                // page se fige au bout de quelques lignes.
                                setOnTouchListener { view, event ->
                                    if (event.actionMasked == MotionEvent.ACTION_DOWN) {
                                        view.parent?.requestDisallowInterceptTouchEvent(true)
                                    }
                                    false
                                }
                                webViewClient = object : WebViewClient() {
                                    override fun shouldOverrideUrlLoading(
                                        view: WebView,
                                        request: WebResourceRequest,
                                    ): Boolean = onLink(request.url)

                                    override fun onPageFinished(view: WebView, url: String) {
                                        scrollToPendingAnchor(view, pendingAnchor)
                                    }
                                }
                                webView = this
                            }
                        },
                        update = { wv ->
                            if (wv.tag != html) {
                                wv.tag = html
                                wv.loadDataWithBaseURL(BASE_URL, html, "text/html", "utf-8", null)
                            }
                        },
                    )
                    if (tab == 1) {
                        TextField(
                            value = text,
                            onValueChange = { text = it },
                            modifier = Modifier
                                .fillMaxSize()
                                .background(MaterialTheme.colorScheme.background),
                            textStyle = TextStyle(
                                fontFamily = FontFamily.Monospace,
                                fontSize = 14.sp,
                            ),
                            colors = TextFieldDefaults.colors(
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent,
                            ),
                        )
                    }
                }
            }
        }
    }
}

/** Rejoint l'ancre demandée par le lien suivi, une fois la page rendue. */
private fun scrollToPendingAnchor(view: WebView, pending: MutableState<String?>) {
    val anchor = pending.value ?: return
    pending.value = null
    val escaped = anchor.replace("\\", "\\\\").replace("'", "\\'")
    view.evaluateJavascript(
        "var el = document.getElementById('$escaped');" +
            "if (el) el.scrollIntoView({block:'start'});",
        null,
    )
}

@Composable
private fun SearchRow(
    query: String,
    onQueryChange: (String) -> Unit,
    onPrevious: () -> Unit,
    onNext: () -> Unit,
    onClose: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        TextField(
            value = query,
            onValueChange = onQueryChange,
            modifier = Modifier.weight(1f),
            placeholder = { Text("Rechercher…") },
            singleLine = true,
        )
        IconButton(onClick = onPrevious) {
            Icon(Icons.Filled.KeyboardArrowUp, contentDescription = "Précédent")
        }
        IconButton(onClick = onNext) {
            Icon(Icons.Filled.KeyboardArrowDown, contentDescription = "Suivant")
        }
        IconButton(onClick = onClose) {
            Icon(Icons.Filled.Close, contentDescription = "Fermer")
        }
    }
}
