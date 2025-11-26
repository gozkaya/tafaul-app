# Tafa'ul (تَفَاؤُل) - Quran Random Verse Generator

A beautiful mobile app that displays random verses from the Holy Quran with translations in 13 languages.

## Features

✅ **Random Verse Selection** - Get random verses from all 114 Surahs (6236 verses)

✅ **13 Language Translations:**
- English (🇬🇧)
- العربية / Arabic (🇸🇦)
- Türkçe / Turkish (🇹🇷)
- اردو / Urdu (🇵🇰)
- Deutsch / German (🇩🇪)
- Français / French (🇫🇷)
- Svenska / Swedish (🇸🇪)
- Suomi / Finnish (🇫🇮)
- Norsk / Norwegian (🇳🇴)
- Nederlands / Dutch (🇳🇱)
- Español / Spanish (🇪🇸)
- 中文 / Chinese (🇨🇳)
- Русский / Russian (🇷🇺)

✅ **Beautiful UI Design:**
- Clean, minimalist interface
- Country-themed colors for each language
- Proper RTL (Right-to-Left) formatting for Arabic text
- Elegant typography

✅ **Smart Features:**
- Welcome screen on app startup
- Language preference persistence (remembers your last selected language)
- Toast notifications on language change
- Share functionality to share verses
- Loading states for better UX

✅ **Mobile Optimized:**
- Responsive design
- Touch-friendly interface
- Smooth animations
- Safe area handling

## How to Use

1. **Launch the App** - You'll see a beautiful welcome screen
2. **Click "Enter"** - Enter the main app
3. **Read the Verse** - A random verse will be displayed in English by default
4. **Change Language** - Tap the language button (with flag) at the top right to select a different language
5. **New Verse** - Tap "New Random Verse" button to get a new random verse
6. **Share** - Tap the "Share" button to share the verse with others

## Technical Details

### Frontend Stack
- **Framework:** React Native with Expo
- **Navigation:** Expo Router (file-based routing)
- **Storage:** AsyncStorage for language persistence
- **Share:** Expo Sharing for native share functionality
- **Icons:** Expo Vector Icons (Ionicons)

### Backend API
- **API Base:** https://verse-translator.preview.emergentagent.com/api
- **Endpoints:**
  - `GET /random-verse?language={code}` - Get random verse with translation
  - `GET /languages` - Get list of supported languages

### Features Implemented

1. **Welcome Screen**
   - Beautiful introductory screen
   - Arabic title (تَفَاؤُل)
   - Enter button with smooth transition

2. **Main Screen**
   - Arabic text displayed prominently with RTL formatting
   - Translation below with language label
   - Surah name and Ayah number reference
   - Share and New Random Verse buttons

3. **Language Selector**
   - Modal bottom sheet design
   - All 13 languages with flag icons
   - Country-themed color indicators
   - Visual selection feedback

4. **Toast Notifications**
   - Shows when language is changed
   - Auto-dismisses after 3 seconds
   - Matches selected language color theme

5. **Persistence**
   - Remembers last selected language
   - Automatically loads on app restart

6. **Share Functionality**
   - Share verses with Arabic text and translation
   - Works on mobile and web platforms
   - Includes verse reference

## Color Themes by Language

Each language has a unique color theme based on their country's flag:

- 🇬🇧 English: Red & Blue
- 🇸🇦 Arabic: Green & White
- 🇹🇷 Turkish: Red & White
- 🇵🇰 Urdu: Green & White
- 🇩🇪 German: Red & Gold
- 🇫🇷 French: Blue & Red
- 🇸🇪 Swedish: Blue & Yellow
- 🇫🇮 Finnish: Blue & White
- 🇳🇴 Norwegian: Red & Blue
- 🇳🇱 Dutch: Orange & Blue
- 🇪🇸 Spanish: Red & Gold
- 🇨🇳 Chinese: Red & Yellow
- 🇷🇺 Russian: Blue & Red

## App Structure

```
frontend/
├── app/
│   └── index.tsx          # Main app file with all features
├── assets/
│   └── images/
├── package.json
└── .env
```

## Running the App

The app is already running and accessible at:
- **Web Preview:** https://tafaul-random.preview.emergentagent.com

### Development Commands

```bash
# Start Expo
cd /app/frontend
yarn start

# Restart Expo service
sudo supervisorctl restart expo
```

## Dependencies

- `react-native` - Core React Native framework
- `expo` - Expo development platform
- `expo-router` - File-based routing
- `@react-native-async-storage/async-storage` - Local storage
- `expo-sharing` - Native share functionality
- `@expo/vector-icons` - Icon library
- `react-native-safe-area-context` - Safe area handling

## Future Enhancements (Optional)

- [ ] Bookmark favorite verses
- [ ] Search verses by Surah or keyword
- [ ] Audio recitation of verses
- [ ] Daily verse notifications
- [ ] Dark mode support
- [ ] Verse history
- [ ] Custom font size adjustment

## Credits

- **API:** Verse Translator API
- **Design:** Minimalist, elegant UI inspired by Islamic art
- **Typography:** System fonts optimized for readability

---

**May peace and blessings be upon you.**

*Tafa'ul (تَفَاؤُل) means "optimism" or "good omen" in Arabic*
