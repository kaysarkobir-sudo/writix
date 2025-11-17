
package com.writixai.games

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class CalculatorActivity : AppCompatActivity() {

    private lateinit var display: TextView
    private lateinit var resultDisplay: TextView

    private var currentInput = ""
    private var operator = ""
    private var firstOperand = ""
    private var isNewOperation = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        // Initialize displays
        display = findViewById(R.id.display)
        resultDisplay = findViewById(R.id.resultDisplay)

        // Number buttons
        val numberButtons = listOf(
            R.id.btn0, R.id.btn1, R.id.btn2, R.id.btn3, R.id.btn4,
            R.id.btn5, R.id.btn6, R.id.btn7, R.id.btn8, R.id.btn9
        )

        numberButtons.forEachIndexed { index, id ->
            findViewById<Button>(id).setOnClickListener {
                onNumberClick(index.toString())
            }
        }

        // Operator buttons
        findViewById<Button>(R.id.btnAdd).setOnClickListener { onOperatorClick("+") }
        findViewById<Button>(R.id.btnSubtract).setOnClickListener { onOperatorClick("-") }
        findViewById<Button>(R.id.btnMultiply).setOnClickListener { onOperatorClick("×") }
        findViewById<Button>(R.id.btnDivide).setOnClickListener { onOperatorClick("÷") }

        // Function buttons
        findViewById<Button>(R.id.btnEquals).setOnClickListener { onEqualsClick() }
        findViewById<Button>(R.id.btnClear).setOnClickListener { onClearClick() }
        findViewById<Button>(R.id.btnDelete).setOnClickListener { onDeleteClick() }
        findViewById<Button>(R.id.btnDecimal).setOnClickListener { onDecimalClick() }

        // Back button
        findViewById<Button>(R.id.btnBack).setOnClickListener {
            finish()
        }

        updateDisplay()
    }

    private fun onNumberClick(number: String) {
        if (isNewOperation) {
            currentInput = number
            isNewOperation = false
        } else {
            currentInput += number
        }
        updateDisplay()
    }

    private fun onOperatorClick(op: String) {
        if (currentInput.isEmpty() && firstOperand.isEmpty()) return

        if (firstOperand.isNotEmpty() && currentInput.isNotEmpty() && operator.isNotEmpty()) {
            // Calculate previous operation first
            calculateResult()
        }

        if (currentInput.isNotEmpty()) {
            firstOperand = currentInput
            currentInput = ""
        }
        operator = op
        isNewOperation = false
        updateDisplay()
    }

    private fun onEqualsClick() {
        if (firstOperand.isEmpty() || currentInput.isEmpty() || operator.isEmpty()) return

        calculateResult()
        operator = ""
        firstOperand = ""
        isNewOperation = true
    }

    private fun calculateResult() {
        try {
            val first = firstOperand.toDouble()
            val second = currentInput.toDouble()

            val result = when (operator) {
                "+" -> first + second
                "-" -> first - second
                "×" -> first * second
                "÷" -> {
                    if (second == 0.0) {
                        resultDisplay.text = "Error: Division by zero"
                        currentInput = ""
                        firstOperand = ""
                        operator = ""
                        updateDisplay()
                        return
                    }
                    first / second
                }
                else -> return
            }

            // Format result: remove .0 for whole numbers
            currentInput = if (result % 1 == 0.0) {
                result.toLong().toString()
            } else {
                result.toString()
            }

            resultDisplay.text = currentInput

        } catch (e: Exception) {
            resultDisplay.text = "Error"
            currentInput = ""
            firstOperand = ""
            operator = ""
        }
        updateDisplay()
    }

    private fun onClearClick() {
        currentInput = ""
        operator = ""
        firstOperand = ""
        isNewOperation = true
        resultDisplay.text = ""
        updateDisplay()
    }

    private fun onDeleteClick() {
        if (currentInput.isNotEmpty()) {
            currentInput = currentInput.dropLast(1)
            updateDisplay()
        }
    }

    private fun onDecimalClick() {
        if (isNewOperation) {
            currentInput = "0."
            isNewOperation = false
        } else if (!currentInput.contains(".")) {
            currentInput += if (currentInput.isEmpty()) "0." else "."
        }
        updateDisplay()
    }

    private fun updateDisplay() {
        val displayText = buildString {
            if (firstOperand.isNotEmpty()) {
                append(firstOperand)
                append(" $operator ")
            }
            append(currentInput)
        }
        display.text = if (displayText.isEmpty()) "0" else displayText
    }
}
