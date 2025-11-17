# Calculator Setup Instructions

## Overview
A fully functional calculator has been created for your Android app with the following features:
- Basic arithmetic operations: addition (+), subtraction (-), multiplication (×), division (÷)
- Decimal number support
- Clear (C) and Delete (⌫) functions
- Real-time display of operations
- Error handling (e.g., division by zero)
- Clean, modern UI with color-coded buttons

## Files Created
1. **CalculatorActivity.kt** - Main calculator logic and functionality
2. **CALCULATOR_LAYOUT.xml** - UI layout for the calculator
3. **MainActivity.kt** - Updated to include calculator navigation

## Setup Steps

### Step 1: Add Layout File
Copy the contents of `CALCULATOR_LAYOUT.xml` to your Android Studio project:
- Create a new file at: `res/layout/activity_calculator.xml`
- Paste the entire XML content from `CALCULATOR_LAYOUT.xml`

### Step 2: Update Bottom Navigation Menu
Add a calculator item to your bottom navigation menu XML (usually at `res/menu/bottom_nav_menu.xml`):

```xml
<item
    android:id="@+id/nav_calculator"
    android:icon="@android:drawable/ic_menu_edit"
    android:title="Calculator" />
```

**Full menu example:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/nav_games"
        android:icon="@android:drawable/ic_menu_gallery"
        android:title="Games" />
    <item
        android:id="@+id/nav_calculator"
        android:icon="@android:drawable/ic_menu_edit"
        android:title="Calculator" />
    <item
        android:id="@+id/nav_about"
        android:icon="@android:drawable/ic_menu_info_details"
        android:title="About" />
</menu>
```

### Step 3: Update AndroidManifest.xml
Add the CalculatorActivity to your `AndroidManifest.xml` file:

```xml
<activity
    android:name=".CalculatorActivity"
    android:label="Calculator"
    android:screenOrientation="portrait" />
```

**Full example:**
```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:theme="@style/AppTheme">

    <activity android:name=".MainActivity">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>

    <activity android:name=".AboutActivity" />
    <activity android:name=".WebActivity" />

    <!-- Add this new activity -->
    <activity
        android:name=".CalculatorActivity"
        android:label="Calculator"
        android:screenOrientation="portrait" />
</application>
```

### Step 4: Copy Kotlin Files
Make sure these Kotlin files are in your project's package directory (e.g., `app/src/main/java/com/writixai/games/`):
- CalculatorActivity.kt
- MainActivity.kt (updated version)

### Step 5: Build and Run
1. Sync your Gradle project in Android Studio
2. Build the project (Build → Make Project)
3. Run on your device or emulator

## How to Use the Calculator

### Navigation
- Tap the "Calculator" icon in the bottom navigation bar to open the calculator
- Use the "← Back" button to return to the main app

### Operations
- **Number buttons (0-9)**: Enter numbers
- **Operator buttons (+, -, ×, ÷)**: Perform operations
- **Decimal (.)**: Add decimal point
- **Equals (=)**: Calculate result
- **Clear (C)**: Clear all input and reset
- **Delete (⌫)**: Delete last character

### Examples
- **Simple calculation**: `5 + 3 =` → Result: 8
- **Decimal numbers**: `3.5 × 2 =` → Result: 7
- **Chain operations**: `10 + 5 × 2 =` → Calculates step by step
- **Division by zero**: Shows "Error: Division by zero"

## UI Features
- **Color-coded buttons**:
  - Red (C button) - Clear
  - Orange (⌫ button) - Delete
  - Cyan (operators) - Operations (+, -, ×, ÷)
  - Green (= button) - Equals
  - Default (numbers) - Number input

- **Two displays**:
  - Top display: Shows current operation (e.g., "5 + 3")
  - Bottom display: Shows result after pressing equals

## Troubleshooting

### Build Errors
- **R.layout.activity_calculator not found**: Make sure you created the layout file in the correct location
- **R.id.nav_calculator not found**: Update your bottom navigation menu XML
- **Activity not declared**: Add CalculatorActivity to AndroidManifest.xml

### Runtime Errors
- **App crashes on calculator button**: Verify all button IDs in the layout match the IDs used in CalculatorActivity.kt
- **Back button doesn't work**: Ensure button ID is `btnBack` in the layout

## Customization

### Change Button Colors
Edit the `android:backgroundTint` attribute in the layout XML:
```xml
<Button
    android:id="@+id/btnAdd"
    android:backgroundTint="#YOUR_COLOR_HERE"
    ... />
```

### Change Display Size
Modify `android:textSize` in the display TextViews:
```xml
<TextView
    android:id="@+id/display"
    android:textSize="32sp"
    ... />
```

### Change Calculator Icon
Replace `android:icon="@android:drawable/ic_menu_edit"` in the bottom navigation menu with your custom icon:
```xml
<item
    android:id="@+id/nav_calculator"
    android:icon="@drawable/ic_calculator"
    android:title="Calculator" />
```

## Support
If you encounter any issues, please check:
1. All files are in the correct locations
2. Package name matches across all files
3. All required IDs are present in layout files
4. Activity is declared in AndroidManifest.xml

Happy calculating! 🧮
