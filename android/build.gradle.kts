// Plugins déclarés au niveau racine, appliqués dans le module :app.
// Kotlin 2.1+ est nécessaire : les versions antérieures refusent de démarrer
// sur le JDK 25 fourni par Android Studio (JavaVersion.parse « 25.0.2 »).
plugins {
    id("com.android.application") version "8.13.2" apply false
    id("org.jetbrains.kotlin.android") version "2.1.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.20" apply false
}
