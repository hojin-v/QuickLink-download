pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
plugins { id("com.android.library") version "9.1.0" apply false }
dependencyResolutionManagement { repositories { google(); mavenCentral() } }
rootProject.name = "QuickLinkSpake2"
include(":spake2")
project(":spake2").projectDir = file("..")
