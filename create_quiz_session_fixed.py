@login_required
@csrf_exempt
def create_quiz_session(request):
    """
    Create a new quiz session.

    - If called via AJAX/Fetch from quiz-orbit (JSON body), this is the API
      behind /dashboard/api/quiz/generate/.
    - If called via regular form POST, it behaves like the original
      "alternative to API endpoint" form view.

    Supports two source types:
        - database  -> Course / Chapter Database (existing logic)
        - knowledge -> Global Knowledge (no course/chapters required)
    """

    # Helper: boolean normalizer
    def _to_bool(value, default=False):
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        return str(value).lower() in ("1", "true", "yes", "on")

    # Helper: detect JSON vs form
    def _get_data(request):
        is_json = (
            request.content_type.startswith("application/json")
            or request.headers.get("Content-Type", "").startswith("application/json")
        )
        if is_json:
            try:
                data = json.loads(request.body or "{}")
            except json.JSONDecodeError:
                return {}, True, "Invalid JSON payload"
            return data, True, None
        return request.POST, False, None

    if request.method == "POST":
        try:
            data, is_json, parse_error = _get_data(request)
            if parse_error:
                return JsonResponse({"error": parse_error}, status=400)

            # Common fields
            title = (data.get("title") or "").strip()
            language = (data.get("language") or "English").strip()
            question_type = data.get("question_type")

            try:
                number = int(data.get("number", 10) or 10)
            except (TypeError, ValueError):
                number = 10

            time_limit_raw = data.get("time_limit")
            show_answers = _to_bool(data.get("show_answers", True), default=True)
            allow_retake = _to_bool(data.get("allow_retake", False), default=False)

            source_type = (data.get("source_type") or "database").strip().lower()

            # Basic validation
            if not title or not question_type:
                return JsonResponse({"error": "Missing required fields: title and question_type are required"}, status=400)

            if number < 5 or number > 100:
                return JsonResponse(
                    {"error": "Number of questions must be between 5 and 100"},
                    status=400,
                )

            # Prepare variable placeholders (both modes)
            course = None
            category = None
            chapter_ids = []

            # =======================
            # SECTION 1 — DATABASE
            # =======================
            if source_type == "database":
                category_id = data.get("category_id")
                course_id = data.get("course_id")

                if is_json:
                    chapter_ids = data.get("chapter_ids") or []
                else:
                    chapter_ids = request.POST.getlist("chapter_ids")

                # strict DB validation - FIXED: Check chapter_ids separately
                if not title:
                    return JsonResponse({"error": "Missing required field: title"}, status=400)
                if not category_id:
                    return JsonResponse({"error": "Missing required field: category_id"}, status=400)
                if not course_id:
                    return JsonResponse({"error": "Missing required field: course_id"}, status=400)
                if not chapter_ids:
                    return JsonResponse({"error": "Missing required field: chapter_ids (at least one chapter must be selected)"}, status=400)
                if not question_type:
                    return JsonResponse({"error": "Missing required field: question_type"}, status=400)

                course = get_object_or_404(VideoCourse, id=course_id)
                category = get_object_or_404(VideoCourseCategory, id=category_id)

                # Gather all chapter content
                all_content = []
                for chap_id in chapter_ids:
                    try:
                        chapter = VideoCourseChapter.objects.get(
                            id=chap_id, course_id=course_id
                        )
                        transcript = getattr(chapter, "transcript", None)
                        if transcript and transcript.text:
                            all_content.append(transcript.text)
                        elif chapter.content:
                            all_content.append(chapter.content)
                    except VideoCourseChapter.DoesNotExist:
                        logger.warning(f"Chapter ID {chap_id} not found")

                if not all_content:
                    return JsonResponse(
                        {"error": "No content found for selected chapters"}, status=400
                    )

                combined = "\n\n---\n\n".join(all_content)
                snippet = combined[:4000]

                ai_prompt = f"""
Based on the course/chapter content below, generate {number} {question_type} questions in {language}.

Course Title: "{course.title}"
Category: "{category.name if category else ''}"

Content: "{snippet}"

CRITICAL: Output MUST be valid JSON in this exact format:
```json
{{
    "questions": [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Why this is correct"
        }}
    ]
}}
```
For MCQ: Include 4 options.
For True/False: Use ["True","False"].
For Fill in the Blanks: Put "______" in question, correct answer in correct_answer.
"""
            # =======================
            # SECTION 2 — GLOBAL KNOWLEDGE
            # =======================
            else:
                knowledge_topic = (data.get("knowledge_topic") or "").strip()
                knowledge_focus = (data.get("knowledge_focus") or "").strip()

                if not knowledge_topic:
                    return JsonResponse({"error": "Missing required field: knowledge_topic"}, status=400)

                focus_part = (
                    f" with a specific focus on: {knowledge_focus}"
                    if knowledge_focus
                    else ""
                )

                ai_prompt = f"""
You are an expert teacher creating {question_type} questions in {language}.

Topic / Subject: "{knowledge_topic}"{focus_part}

Generate {number} high-quality questions suitable for a quiz.

CRITICAL: Output MUST be valid JSON in this exact format:

{{
    "questions": [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Why this is correct"
        }}
    ]
}}

For MCQ: Include 4 options.
For True/False: Use ["True","False"].
For Fill in the Blanks: Put "______" in question.
"""

                # no chapters for knowledge mode
                chapter_ids = []

            # =======================
            # SECTION 3 — AI GENERATION
            # =======================
            try:
                gen_text, gen_model, _ = ai_generate_text_responses(
                    client=client,
                    system_prompt=(
                        f"You are an expert teacher creating {question_type} "
                        f"questions in {language}. Output only valid JSON."
                    ),
                    user_prompt=ai_prompt,
                    use_case="create_quiz_session",
                    extra_kwargs={},
                )
            except AIServiceError as e:
                logger.exception("Error generating quiz with AI")
                return JsonResponse({"error": str(e)}, status=500)

            from .utils import _extract_json_from_text, generate_access_code

            extracted_json = _extract_json_from_text(gen_text or "")
            if not extracted_json:
                return JsonResponse(
                    {"error": "AI response not in valid JSON format"}, status=500
                )

            try:
                questions_data = json.loads(extracted_json)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"error": "Failed to parse AI response"}, status=500
                )

            access_code = generate_access_code()

            time_limit_int = None
            if time_limit_raw not in (None, "", "null"):
                try:
                    time_limit_int = int(time_limit_raw)
                except (TypeError, ValueError):
                    time_limit_int = None

            # =======================
            # SECTION 4 — CREATE SESSION
            # =======================
            quiz_session = QuizSession.objects.create(
                teacher=request.user,
                title=title,
                category=category,
                course=course,
                chapter_ids=chapter_ids,
                language=language,
                question_type=question_type,
                total_questions=number,
                time_limit=time_limit_int,
                questions_data=questions_data,
                access_code=access_code,
                show_answers=show_answers,
                allow_retake=allow_retake,
                unique_code=uuid.uuid4(),
            )

            logger.info(
                f"✅ Created quiz session: {quiz_session.unique_code} "
                f"by {request.user.username}"
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or is_json:
                return JsonResponse(
                    {
                        "success": True,
                        "quiz_code": str(quiz_session.unique_code),
                        "access_code": access_code,
                        "message": (
                            f"Quiz created successfully! Access Code: {access_code}"
                        ),
                    }
                )

            messages.success(
                request, f"Quiz created successfully! Access Code: {access_code}"
            )
            return redirect(
                "dashboard:view_quiz_results", session_code=quiz_session.unique_code
            )

        except Exception as e:
            logger.exception("Error in create_quiz_session")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"error": str(e)}, status=500)
            messages.error(request, f"Error creating quiz: {str(e)}")
            return redirect("dashboard:quiz_dashboard_upgraded")

    # GET
    return render(request, "dashboard/custom-gpt/quiz/create.html")
