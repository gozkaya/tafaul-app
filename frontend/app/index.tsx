import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Platform,
  Dimensions,
  Modal,
  Pressable,
  Alert,
  Share
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Sharing from 'expo-sharing';
import { Ionicons } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

const API_BASE = 'https://verse-translator.preview.emergentagent.com/api';

// Language configurations with country colors (sorted alphabetically)
const LANGUAGES = [
  { code: 'ar', name: 'العربية', flag: '🇸🇦', colors: ['#165B33', '#FFFFFF'] },
  { code: 'zh', name: '中文', flag: '🇨🇳', colors: ['#DE2910', '#FFDE00'] },
  { code: 'nl', name: 'Nederlands', flag: '🇳🇱', colors: ['#FF6600', '#21468B'] },
  { code: 'en', name: 'English', flag: '🇬🇧', colors: ['#C8102E', '#012169'] },
  { code: 'fi', name: 'Suomi', flag: '🇫🇮', colors: ['#003580', '#FFFFFF'] },
  { code: 'fr', name: 'Français', flag: '🇫🇷', colors: ['#0055A4', '#EF4135'] },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪', colors: ['#DD0000', '#FFCE00'] },
  { code: 'no', name: 'Norsk', flag: '🇳🇴', colors: ['#BA0C2F', '#00205B'] },
  { code: 'ru', name: 'Русский', flag: '🇷🇺', colors: ['#0039A6', '#D52B1E'] },
  { code: 'es', name: 'Español', flag: '🇪🇸', colors: ['#AA151B', '#F1BF00'] },
  { code: 'sv', name: 'Svenska', flag: '🇸🇪', colors: ['#006AA7', '#FECC00'] },
  { code: 'tr', name: 'Türkçe', flag: '🇹🇷', colors: ['#E30A17', '#FFFFFF'] },
  { code: 'uk', name: 'Українська', flag: '🇺🇦', colors: ['#005BBB', '#FFD500'] },
  { code: 'ur', name: 'اردو', flag: '🇵🇰', colors: ['#01411C', '#FFFFFF'] },
];

interface Verse {
  surah_number: number;
  surah_name: string;
  surah_name_arabic: string;
  verse_number: number;
  arabic_text: string;
  translation: string;
  language: string;
  reference: string;
}

interface ToastMessage {
  message: string;
  visible: boolean;
}

export default function Index() {
  const [showWelcome, setShowWelcome] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState(LANGUAGES.find(l => l.code === 'en') || LANGUAGES[0]);
  const [verse, setVerse] = useState<Verse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [toast, setToast] = useState<ToastMessage>({ message: '', visible: false });
  const [initialLoading, setInitialLoading] = useState(true);

  // Load saved language preference and fetch initial verse
  useEffect(() => {
    loadSavedLanguage();
  }, []);

  const loadSavedLanguage = async () => {
    try {
      const savedLangCode = await AsyncStorage.getItem('selectedLanguage');
      if (savedLangCode) {
        const lang = LANGUAGES.find(l => l.code === savedLangCode);
        if (lang) {
          setSelectedLanguage(lang);
        }
      }
    } catch (error) {
      console.error('Error loading saved language:', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const fetchRandomVerse = async (langCode: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/random-verse?language=${langCode}`);
      if (!response.ok) {
        throw new Error('Failed to fetch verse');
      }
      const data = await response.json();
      setVerse(data);
    } catch (error) {
      console.error('Error fetching verse:', error);
      showToast('Failed to fetch verse. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = async (lang: typeof LANGUAGES[0]) => {
    setSelectedLanguage(lang);
    setShowLanguageModal(false);
    
    // Save language preference
    try {
      await AsyncStorage.setItem('selectedLanguage', lang.code);
    } catch (error) {
      console.error('Error saving language:', error);
    }

    // Re-translate current verse if exists
    if (verse) {
      await fetchRandomVerse(lang.code);
      showToast(`Language changed to ${lang.name}`);
    }
  };

  const handleNewVerse = () => {
    fetchRandomVerse(selectedLanguage.code);
  };

  const handleClearVerse = () => {
    setVerse(null);
  };

  const showToast = (message: string) => {
    setToast({ message, visible: true });
    setTimeout(() => {
      setToast({ message: '', visible: false });
    }, 3000);
  };

  const handleShare = async () => {
    if (!verse) return;

    const shareText = `${verse.arabic_text}\n\n${verse.translation}\n\n— ${verse.reference}\n\nShared from Tafa'ul (تَفَاؤُل) App`;

    try {
      if (Platform.OS === 'web') {
        // Web share API
        if (navigator.share) {
          await navigator.share({
            text: shareText,
          });
        } else {
          // Fallback for web
          await navigator.clipboard.writeText(shareText);
          showToast('Verse copied to clipboard!');
        }
      } else {
        // Mobile share
        await Share.share({
          message: shareText,
        });
      }
    } catch (error: any) {
      if (error.message !== 'User did not share') {
        console.error('Error sharing:', error);
        showToast('Failed to share verse');
      }
    }
  };

  const handleEnterApp = () => {
    setShowWelcome(false);
  };

  // Welcome Screen
  if (showWelcome) {
    return (
      <SafeAreaView style={styles.welcomeContainer}>
        <ScrollView 
          contentContainerStyle={styles.welcomeScrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.welcomeContent}>
            <Text style={styles.welcomeTitle}>TAFAUL</Text>
            <Text style={styles.welcomeSubtitleArabic}>تَفَاؤُل</Text>
            <Text style={styles.welcomeDescription}>
              Random Verse from the Holy Quran
            </Text>
            <Text style={styles.welcomeDescription2}>
              Find peace and guidance through divine verses
            </Text>
            
            <View style={styles.disclaimerContainer}>
              <Text style={styles.disclaimerTitle}>What is Tafa'ul?</Text>
              <Text style={styles.disclaimerText}>
                Tafa'ul (تَفَاؤُل) means "optimism" or "seeking a good omen" in Arabic. It is a practice where one opens the Quran randomly, seeking guidance, comfort, or inspiration from Allah's words.
              </Text>
              <Text style={styles.disclaimerText}>
                The Prophet Muhammad (peace be upon him) loved optimism and encouraged positive thinking. While Tafa'ul with the Quran is not a method of fortune-telling, many Muslims find solace and reflection through random verses, believing that Allah's guidance can reach us in unexpected ways.
              </Text>
              <Text style={styles.disclaimerNote}>
                "Indeed, in the remembrance of Allah do hearts find rest." - Quran 13:28
              </Text>
            </View>
            
            <TouchableOpacity
              style={styles.enterButton}
              onPress={handleEnterApp}
              activeOpacity={0.8}
            >
              <Text style={styles.enterButtonText}>Enter</Text>
              <Ionicons name="arrow-forward" size={20} color="#FFF" />
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Initial loading
  if (initialLoading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#165B33" />
        <Text style={styles.loadingText}>Loading...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.appTitle}>TAFAUL</Text>
          <TouchableOpacity
            style={[styles.languageButton, { 
              borderColor: selectedLanguage.colors[0],
              backgroundColor: selectedLanguage.colors[0] + '10'
            }]}
            onPress={() => setShowLanguageModal(true)}
            activeOpacity={0.7}
          >
            <Text style={styles.flagIcon}>{selectedLanguage.flag}</Text>
            <Text style={[styles.languageButtonText, { color: selectedLanguage.colors[0] }]}>
              {selectedLanguage.name}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Action Buttons at Top */}
        <View style={styles.topActionsContainer}>
          <TouchableOpacity
            style={[styles.topActionButton, styles.newVerseButton, {
              backgroundColor: selectedLanguage.colors[0],
              flex: 1,
            }]}
            onPress={handleNewVerse}
            activeOpacity={0.8}
            disabled={loading}
          >
            <Ionicons name="refresh" size={20} color="#FFF" />
            <Text style={styles.newVerseButtonText}>New Random Verse</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.topActionButton, styles.clearButton]}
            onPress={handleClearVerse}
            activeOpacity={0.8}
          >
            <Ionicons name="close-circle-outline" size={20} color="#666" />
            <Text style={styles.clearButtonText}>Clear</Text>
          </TouchableOpacity>
        </View>

        {/* Verse Display */}
        {loading ? (
          <View style={styles.loadingVerseContainer}>
            <ActivityIndicator size="large" color={selectedLanguage.colors[0]} />
            <Text style={[styles.loadingVerseText, { color: selectedLanguage.colors[0] }]}>
              Loading verse...
            </Text>
          </View>
        ) : verse ? (
          <View>
            <View style={styles.verseContainer}>
              {/* Arabic Text */}
              <View style={styles.arabicSection}>
                <Text style={styles.arabicText}>{verse.arabic_text}</Text>
              </View>

              {/* Divider */}
              <View style={[styles.divider, { backgroundColor: selectedLanguage.colors[0] }]} />

              {/* Translation */}
              <View style={styles.translationSection}>
                <Text style={styles.languageLabel}>{selectedLanguage.name} Translation</Text>
                <Text style={styles.translationText}>{verse.translation}</Text>
              </View>

              {/* Reference */}
              <View style={styles.referenceSection}>
                <Text style={[styles.referenceText, { color: selectedLanguage.colors[0] }]}>
                  {verse.reference}
                </Text>
                <Text style={styles.surahNameArabic}>{verse.surah_name_arabic}</Text>
              </View>
            </View>

            {/* Share Button */}
            <TouchableOpacity
              style={[styles.shareButton]}
              onPress={handleShare}
              activeOpacity={0.8}
            >
              <Ionicons name="share-social-outline" size={20} color="#666" />
              <Text style={styles.shareButtonText}>Share Verse</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.emptyStateContainer}>
            <Ionicons name="book-outline" size={80} color="#CCC" />
            <Text style={styles.emptyStateText}>No verse selected</Text>
            <Text style={styles.emptyStateSubtext}>Tap "New Random Verse" to get started</Text>
          </View>
        )}
      </ScrollView>

      {/* Language Selection Modal */}
      <Modal
        visible={showLanguageModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowLanguageModal(false)}
      >
        <Pressable 
          style={styles.modalOverlay}
          onPress={() => setShowLanguageModal(false)}
        >
          <Pressable style={styles.modalContent} onPress={(e) => e.stopPropagation()}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Select Language</Text>
              <TouchableOpacity onPress={() => setShowLanguageModal(false)}>
                <Ionicons name="close" size={28} color="#333" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.languageList}>
              {LANGUAGES.map((lang) => (
                <TouchableOpacity
                  key={lang.code}
                  style={[
                    styles.languageItem,
                    selectedLanguage.code === lang.code && styles.languageItemSelected,
                    { borderLeftColor: lang.colors[0], borderLeftWidth: 4 }
                  ]}
                  onPress={() => handleLanguageChange(lang)}
                  activeOpacity={0.7}
                >
                  <Text style={styles.languageFlag}>{lang.flag}</Text>
                  <Text style={styles.languageName}>{lang.name}</Text>
                  {selectedLanguage.code === lang.code && (
                    <Ionicons name="checkmark-circle" size={24} color={lang.colors[0]} />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>

      {/* Toast Notification */}
      {toast.visible && (
        <View style={[styles.toast, { backgroundColor: selectedLanguage.colors[0] }]}>
          <Text style={styles.toastText}>{toast.message}</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  // Welcome Screen
  welcomeContainer: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  welcomeScrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingVertical: 40,
  },
  welcomeContent: {
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  welcomeTitle: {
    fontSize: 56,
    fontWeight: '700',
    color: '#165B33',
    marginBottom: 8,
    letterSpacing: 4,
  },
  welcomeSubtitleArabic: {
    fontSize: 36,
    fontWeight: '300',
    color: '#666',
    marginBottom: 48,
    letterSpacing: 2,
  },
  welcomeDescription: {
    fontSize: 18,
    color: '#555',
    textAlign: 'center',
    marginBottom: 12,
    fontWeight: '400',
  },
  welcomeDescription2: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginBottom: 64,
  },
  enterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#165B33',
    paddingHorizontal: 48,
    paddingVertical: 16,
    borderRadius: 30,
    gap: 12,
  },
  enterButtonText: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: '600',
    letterSpacing: 1,
  },

  // Main App
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FAFAFA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },

  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 32,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#165B33',
    letterSpacing: 3,
  },
  languageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1.5,
    gap: 8,
  },
  flagIcon: {
    fontSize: 24,
  },
  languageButtonText: {
    fontSize: 14,
    fontWeight: '600',
  },

  // Verse Container
  verseContainer: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  loadingVerseContainer: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 48,
    marginBottom: 24,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 200,
  },
  loadingVerseText: {
    marginTop: 16,
    fontSize: 16,
  },

  // Arabic Section
  arabicSection: {
    marginBottom: 20,
  },
  arabicText: {
    fontSize: 28,
    lineHeight: 48,
    textAlign: 'right',
    color: '#1a1a1a',
    fontWeight: '400',
    writingDirection: 'rtl',
  },

  // Divider
  divider: {
    height: 2,
    width: 60,
    alignSelf: 'center',
    marginVertical: 20,
    borderRadius: 1,
  },

  // Translation Section
  translationSection: {
    marginBottom: 20,
  },
  languageLabel: {
    fontSize: 12,
    color: '#888',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 12,
    fontWeight: '600',
  },
  translationText: {
    fontSize: 18,
    lineHeight: 30,
    color: '#333',
    fontWeight: '400',
  },

  // Reference Section
  referenceSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    alignItems: 'center',
  },
  referenceText: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  surahNameArabic: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },

  // Top Action Buttons
  topActionsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  topActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  newVerseButton: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
  },
  newVerseButtonText: {
    fontSize: 15,
    color: '#FFF',
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  clearButton: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1.5,
    borderColor: '#E0E0E0',
    paddingHorizontal: 20,
  },
  clearButtonText: {
    fontSize: 15,
    color: '#666',
    fontWeight: '600',
  },

  // Share Button (below verse)
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
    marginTop: 16,
  },
  shareButtonText: {
    fontSize: 15,
    color: '#666',
    fontWeight: '600',
  },

  // Empty State
  emptyStateContainer: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 48,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 300,
    marginBottom: 24,
  },
  emptyStateText: {
    fontSize: 20,
    color: '#999',
    fontWeight: '600',
    marginTop: 20,
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#BBB',
    textAlign: 'center',
  },

  // Language Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: height * 0.7,
    paddingBottom: Platform.OS === 'ios' ? 34 : 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  languageList: {
    padding: 8,
  },
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FAFAFA',
    marginVertical: 4,
    marginHorizontal: 8,
    borderRadius: 12,
    gap: 16,
  },
  languageItemSelected: {
    backgroundColor: '#F0F0F0',
  },
  languageFlag: {
    fontSize: 32,
  },
  languageName: {
    fontSize: 16,
    color: '#333',
    flex: 1,
    fontWeight: '500',
  },

  // Toast
  toast: {
    position: 'absolute',
    bottom: 100,
    left: 20,
    right: 20,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 5,
  },
  toastText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
