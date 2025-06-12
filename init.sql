-- Create question_templates table
CREATE TABLE question_templates (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options JSONB,
    order_index INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    keywords JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_question_templates_category ON question_templates(category);
CREATE INDEX idx_question_templates_order ON question_templates(category, order_index);
CREATE INDEX idx_question_templates_type ON question_templates(question_type);

-- Add comments for documentation
COMMENT ON TABLE question_templates IS 'Template questions for different medical categories in pet consultations';
COMMENT ON COLUMN question_templates.category IS 'Medical category (digestive, respiratory, dermatological, etc.)';
COMMENT ON COLUMN question_templates.question_text IS 'The actual question text to display to users';
COMMENT ON COLUMN question_templates.question_type IS 'Type of question: multiple_choice, text, boolean, scale';
COMMENT ON COLUMN question_templates.options IS 'JSON array of options for multiple choice questions';
COMMENT ON COLUMN question_templates.order_index IS 'Order of questions within a category';
COMMENT ON COLUMN question_templates.is_required IS 'Whether this question is mandatory';
COMMENT ON COLUMN question_templates.keywords IS 'JSON array of keywords that trigger this question';

-- Insert sample data
INSERT INTO question_templates (category, question_text, question_type, options, order_index, is_required, keywords) VALUES
-- Digestive category
('digestive', 'How long has your pet been experiencing digestive issues?', 'multiple_choice', '["Less than 24 hours", "1-3 days", "4-7 days", "More than a week"]', 1, true, '["vomiting", "diarrhea", "appetite"]'),
('digestive', 'What does your pet''s stool look like?', 'multiple_choice', '["Normal", "Loose/watery", "Hard/dry", "Contains blood", "Contains mucus"]', 2, true, '["diarrhea", "stool", "bowel"]'),
('digestive', 'Has your pet eaten anything unusual recently?', 'text', null, 3, true, '["eating", "food", "garbage"]'),
('digestive', 'Is your pet drinking more or less water than usual?', 'multiple_choice', '["Much more", "Slightly more", "Normal", "Slightly less", "Much less"]', 4, true, '["water", "drinking", "dehydration"]'),
('digestive', 'Has your pet vomited? If so, what did it look like?', 'text', null, 5, false, '["vomiting", "throw up"]'),

-- Respiratory category
('respiratory', 'What type of cough does your pet have?', 'multiple_choice', '["Dry cough", "Wet/productive cough", "Honking sound", "Gagging", "No cough"]', 1, true, '["cough", "coughing"]'),
('respiratory', 'Is your pet having difficulty breathing?', 'multiple_choice', '["No difficulty", "Mild difficulty", "Moderate difficulty", "Severe difficulty"]', 2, true, '["breathing", "respiratory"]'),
('respiratory', 'Are there any nasal discharge or changes in breathing sounds?', 'text', null, 3, false, '["nose", "nasal", "discharge"]'),
('respiratory', 'Does the breathing difficulty worsen with activity?', 'boolean', null, 4, true, '["breathing", "exercise", "activity"]'),

-- Dermatological category
('dermatological', 'Where on your pet''s body is the skin issue located?', 'multiple_choice', '["Face/head", "Neck", "Back", "Belly", "Legs", "Tail", "All over"]', 1, true, '["skin", "fur", "hair", "rash"]'),
('dermatological', 'How often does your pet scratch or lick the affected area?', 'multiple_choice', '["Rarely", "Occasionally", "Frequently", "Constantly"]', 2, true, '["itching", "scratching", "licking"]'),
('dermatological', 'What does the affected skin look like?', 'multiple_choice', '["Red and inflamed", "Dry and flaky", "Wet and oozing", "Bumpy or raised", "Normal appearance"]', 3, true, '["skin", "appearance", "color"]'),
('dermatological', 'Has your pet been exposed to any new products, foods, or environments?', 'text', null, 4, false, '["allergies", "new", "environment"]'),

-- Musculoskeletal category
('musculoskeletal', 'Which leg or limb is affected?', 'multiple_choice', '["Front left", "Front right", "Back left", "Back right", "Multiple legs", "Not sure"]', 1, true, '["limping", "leg", "paw"]'),
('musculoskeletal', 'When did you first notice the limping?', 'multiple_choice', '["Today", "Yesterday", "2-3 days ago", "This week", "Longer than a week"]', 2, true, '["limping", "mobility"]'),
('musculoskeletal', 'Does your pet show signs of pain when the area is touched?', 'boolean', null, 3, true, '["pain", "touch", "sensitive"]'),
('musculoskeletal', 'Is the limping constant or does it come and go?', 'multiple_choice', '["Constant", "Worse in morning", "Worse after activity", "Comes and goes", "Only occasionally"]', 4, true, '["limping", "frequency"]'),

-- Behavioral category
('behavioral', 'How would you describe the change in your pet''s behavior?', 'multiple_choice', '["More aggressive", "More withdrawn", "More anxious", "Less active", "Restless", "Other"]', 1, true, '["behavior", "aggressive", "anxious"]'),
('behavioral', 'When did you first notice these behavioral changes?', 'multiple_choice', '["Today", "This week", "This month", "Gradually over time"]', 2, true, '["behavioral", "changes"]'),
('behavioral', 'Has there been any change in your pet''s environment or routine?', 'text', null, 3, false, '["environment", "routine", "stress"]'),
('behavioral', 'Is your pet eating and sleeping normally?', 'multiple_choice', '["Both normal", "Eating less, sleeping normal", "Eating normal, sleeping less", "Both affected"]', 4, true, '["eating", "sleeping", "appetite"]'),

-- Emergency category
('emergency', 'What type of emergency situation is this?', 'multiple_choice', '["Trauma/injury", "Suspected poisoning", "Difficulty breathing", "Seizure", "Severe bleeding", "Loss of consciousness", "Other"]', 1, true, '["emergency", "trauma", "poisoning"]'),
('emergency', 'How long ago did this emergency occur?', 'multiple_choice', '["Just now", "Within 1 hour", "1-3 hours ago", "3-6 hours ago", "More than 6 hours"]', 2, true, '["emergency", "when"]'),
('emergency', 'Is your pet conscious and responsive?', 'boolean', null, 3, true, '["consciousness", "responsive"]'),
('emergency', 'Have you contacted or are you planning to contact an emergency vet?', 'boolean', null, 4, true, '["emergency", "vet", "contact"]'),

-- General questions for all categories
('general', 'Has your pet experienced this issue before?', 'boolean', null, 1, true, '[]'),
('general', 'Is your pet currently on any medications?', 'text', null, 2, true, '[]'),
('general', 'Rate your pet''s overall energy level today', 'scale', '["1 (Very low)", "2 (Low)", "3 (Normal)", "4 (High)", "5 (Very high)"]', 3, true, '[]'),
('general', 'When was your pet''s last veterinary checkup?', 'multiple_choice', '["Within 1 month", "1-6 months ago", "6-12 months ago", "More than 1 year ago", "Never"]', 4, false, '[]'),
('general', 'Is your pet up to date on vaccinations?', 'boolean', null, 5, false, '[]');