"""
ATS Scoring Engine - Extracted from ATS_Score_Checker.ipynb
Calculates resume-JD matching scores for job applications
"""

import re
import PyPDF2
from pathlib import Path

# Configuration - DO NOT MODIFY WEIGHTS
SCORING_WEIGHTS = {
    'skill_match': 0.45,
    'experience_fit': 0.25,
    'project_relevance': 0.20,
    'bonus_signals': 0.10
}

# Comprehensive skill database with variations
SKILL_DATABASE = {
    # Programming Languages
    'python': ['python', 'py', 'python3', 'django', 'flask', 'fastapi'],
    'java': ['java', 'j2ee', 'spring', 'springboot', 'hibernate'],
    'javascript': ['javascript', 'js', 'node', 'nodejs', 'node.js', 'typescript', 'ts'],
    'c++': ['c++', 'cpp', 'cplusplus'],
    'c#': ['c#', 'csharp', '.net', 'dotnet', 'asp.net'],
    'go': ['go', 'golang'],
    'rust': ['rust'],
    'php': ['php', 'laravel', 'symfony'],
    'ruby': ['ruby', 'rails', 'ruby on rails'],
    'swift': ['swift', 'ios'],
    'kotlin': ['kotlin', 'android'],
    
    # Web Technologies
    'html': ['html', 'html5'],
    'css': ['css', 'css3', 'sass', 'scss', 'less'],
    'react': ['react', 'reactjs', 'react.js', 'react native', 'redux', 'next.js', 'nextjs'],
    'angular': ['angular', 'angularjs'],
    'vue': ['vue', 'vuejs', 'vue.js', 'nuxt'],
    
    # Databases
    'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mariadb'],
    'mongodb': ['mongodb', 'mongo', 'nosql'],
    'redis': ['redis', 'cache'],
    'elasticsearch': ['elasticsearch', 'elastic'],
    
    # Data Science & ML
    'pandas': ['pandas', 'dataframe'],
    'numpy': ['numpy', 'numerical'],
    'scikit-learn': ['scikit-learn', 'sklearn', 'machine learning', 'ml'],
    'tensorflow': ['tensorflow', 'tf', 'keras'],
    'pytorch': ['pytorch', 'torch'],
    'opencv': ['opencv', 'cv2', 'computer vision'],
    
    # DevOps & Tools
    'docker': ['docker', 'container', 'containerization'],
    'kubernetes': ['kubernetes', 'k8s', 'orchestration'],
    'git': ['git', 'github', 'gitlab', 'version control'],
    'jenkins': ['jenkins', 'ci/cd', 'continuous integration'],
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
    'azure': ['azure', 'microsoft azure'],
    'gcp': ['gcp', 'google cloud', 'google cloud platform'],
    
    # Other Technologies
    'rest': ['rest', 'restful', 'api', 'rest api'],
    'graphql': ['graphql', 'apollo'],
    'agile': ['agile', 'scrum', 'kanban', 'jira'],
    'testing': ['testing', 'test', 'qa', 'quality assurance', 'unit test', 'pytest', 'jest', 'junit', 'selenium', 'cypress'],
}


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""


def extract_text(file_path):
    """Universal text extractor"""
    path = Path(file_path)
    
    if path.suffix.lower() == '.pdf':
        return extract_text_from_pdf(file_path)
    elif path.suffix.lower() == '.docx':
        return extract_text_from_docx(file_path)
    elif path.suffix.lower() == '.txt':
        return open(file_path, 'r', encoding='utf-8').read()
    else:
        return ""


class EnhancedResumeParser:
    """Enhanced parser with comprehensive skill detection"""
    
    def __init__(self, skill_db):
        self.skill_db = skill_db
    
    def parse(self, text):
        text_lower = text.lower()
        
        return {
            "skills": self._extract_skills(text_lower),
            "experience_years": self._extract_years(text_lower),
            "projects": self._extract_projects(text),
            "certifications": self._extract_certifications(text),
            "education": self._extract_education(text_lower)
        }
    
    def _extract_skills(self, text):
        """Extract skills using comprehensive database"""
        found_skills = set()
        
        for skill_name, variations in self.skill_db.items():
            for variation in variations:
                # Use word boundaries for accurate matching
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text):
                    found_skills.add(skill_name)
                    break
        
        return list(found_skills)
    
    def _extract_years(self, text):
        """Extract years of experience with multiple patterns"""
        patterns = [
            r'(\d+\.?\d*)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience',
            r'experience\s*:?\s*(\d+\.?\d*)\s*(?:\+)?\s*years?',
            r'(\d+\.?\d*)\s*(?:\+)?\s*yrs?\s+(?:of\s+)?experience',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def _extract_projects(self, text):
        """Extract project descriptions"""
        projects = []
        lines = text.split('\n')
        
        # Look for project sections
        in_project_section = False
        for line in lines:
            line_lower = line.lower()
            
            # Detect project section headers
            if re.search(r'\b(project|work)\b', line_lower) and len(line) < 50:
                in_project_section = True
                continue
            
            # Collect substantial project lines
            if in_project_section and len(line.strip()) > 40:
                projects.append(line.strip())
                if len(projects) >= 5:
                    break
        
        return projects
    
    def _extract_certifications(self, text):
        """Extract certifications"""
        cert_keywords = [
            'certified', 'certification', 'certificate', 'credential',
            'aws certified', 'google cloud', 'microsoft certified',
            'coursera', 'udemy', 'professional certificate'
        ]
        
        certifications = []
        for line in text.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in cert_keywords):
                certifications.append(line.strip())
        
        return certifications
    
    def _extract_education(self, text):
        """Extract education level"""
        if re.search(r'\b(phd|ph\.d|doctorate)\b', text):
            return 'phd'
        elif re.search(r'\b(master|m\.s|m\.tech|mba)\b', text):
            return 'masters'
        elif re.search(r'\b(bachelor|b\.s|b\.tech|b\.e)\b', text):
            return 'bachelors'
        return 'other'


class EnhancedJDParser:
    """Enhanced JD parser with better requirement extraction"""
    
    def __init__(self, skill_db):
        self.skill_db = skill_db
    
    def parse(self, text):
        text_lower = text.lower()
        
        required, preferred = self._categorize_skills(text_lower)
        
        return {
            "required_skills": required,
            "preferred_skills": preferred,
            "min_experience": self._extract_years(text_lower),
            "role_level": self._extract_level(text_lower)
        }
    
    def _categorize_skills(self, text):
        """Separate required vs preferred skills"""
        required = set()
        preferred = set()
        
        # Look for skills in required section
        req_section = re.search(r'(?:required|must have|essential)[\s\S]*?(?:preferred|nice|optional|$)', text)
        pref_section = re.search(r'(?:preferred|nice to have|optional|bonus)[\s\S]*?(?:$)', text)

        # Treat placeholder required sections as missing so we can fall back to full-text parsing
        if req_section:
            req_blob = req_section.group().strip()
            if re.search(r'\b(not\s+specified|n\/?a|none|tbd)\b', req_blob):
                req_section = None
        
        for skill_name, variations in self.skill_db.items():
            for variation in variations:
                pattern = r'\b' + re.escape(variation) + r'\b'
                
                # Check in required section
                if req_section and re.search(pattern, req_section.group()):
                    required.add(skill_name)
                    break
                
                # Check in preferred section
                if pref_section and re.search(pattern, pref_section.group()):
                    preferred.add(skill_name)
                    break
                
                # If no sections found, check in full text
                if not req_section and not pref_section:
                    if re.search(pattern, text):
                        required.add(skill_name)
                        break

        # If we had sections but extracted nothing, fall back to scanning the full JD text.
        # This prevents near-constant scores when the "Required Skills" block is empty.
        if not required and not preferred:
            for skill_name, variations in self.skill_db.items():
                for variation in variations:
                    pattern = r'\b' + re.escape(variation) + r'\b'
                    if re.search(pattern, text):
                        required.add(skill_name)
                        break

        # If only preferred skills were detected, treat them as requirements for scoring purposes.
        if not required and preferred:
            required = set(preferred)
        
        return list(required), list(preferred)
    
    def _extract_years(self, text):
        """Extract minimum years of experience"""
        patterns = [
            r'(\d+\.?\d*)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience',
            r'minimum\s+(\d+\.?\d*)\s*(?:\+)?\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def _extract_level(self, text):
        """Determine role level"""
        if re.search(r'\b(intern|internship)\b', text):
            return "intern"
        elif re.search(r'\b(entry|junior|fresher|graduate)\b', text):
            return "junior"
        elif re.search(r'\b(mid|intermediate|senior)\b', text):
            return "mid"
        elif re.search(r'\b(lead|principal|architect|staff)\b', text):
            return "senior"
        return "mid"


class ScoringEngine:
    """Scoring engine with fixed weights"""
    
    def __init__(self, weights):
        self.weights = weights
    
    def calculate_skill_score(self, matched, required):
        """Calculate skill match score"""
        if not required:
            return 90.0  # If no requirements, assume good match
        
        match_ratio = len(matched) / len(required)
        
        # Progressive scoring
        if match_ratio >= 0.9:
            return 95.0
        elif match_ratio >= 0.75:
            return 85.0
        elif match_ratio >= 0.6:
            return 75.0
        elif match_ratio >= 0.4:
            return 60.0
        elif match_ratio >= 0.2:
            return 40.0
        else:
            return 20.0
    
    def calculate_experience_score(self, resume_years, required_years):
        """Calculate experience fit score"""
        if required_years == 0:
            return 80.0
        
        if resume_years >= required_years:
            # Bonus for exceeding requirements
            excess = min((resume_years - required_years) / required_years, 0.5)
            return min(100.0, 90.0 + (excess * 20))
        else:
            # Penalty for insufficient experience
            deficit = (required_years - resume_years) / required_years
            return max(30.0, 90.0 - (deficit * 60))
    
    def calculate_project_score(self, projects):
        """Calculate project relevance score"""
        project_count = len(projects)
        
        if project_count >= 4:
            return 90.0
        elif project_count >= 3:
            return 80.0
        elif project_count >= 2:
            return 65.0
        elif project_count >= 1:
            return 50.0
        else:
            return 25.0
    
    def calculate_bonus_score(self, certifications, education, preferred_match_count):
        """Calculate bonus signals score"""
        score = 40.0  # Base score
        
        # Certifications bonus
        if len(certifications) >= 3:
            score += 25.0
        elif len(certifications) >= 1:
            score += 15.0
        
        # Education bonus
        if education == 'phd':
            score += 20.0
        elif education == 'masters':
            score += 15.0
        elif education == 'bachelors':
            score += 10.0
        
        # Preferred skills bonus
        if preferred_match_count >= 3:
            score += 15.0
        elif preferred_match_count >= 1:
            score += 10.0
        
        return min(100.0, score)
    
    def final_score(self, scores):
        """Calculate weighted final score"""
        total = sum(scores[k] * self.weights[k] for k in scores)
        total = round(total, 2)
        
        # Determine readiness level
        if total >= 85:
            level = "Highly Prepared"
            msg = "Excellent alignment with this role"
        elif total >= 70:
            level = "Prepared"
            msg = "Strong alignment, ready to apply"
        elif total >= 55:
            level = "Developing Readiness"
            msg = "Good foundation, some skill gaps to address"
        elif total >= 40:
            level = "Preparation Stage"
            msg = "Basic alignment, significant improvements needed"
        else:
            level = "Early Stage"
            msg = "Role requirements significantly exceed current profile"
        
        return total, level, msg


class ATSMatcher:
    """Main ATS matching engine"""
    
    def __init__(self, skill_db=SKILL_DATABASE, weights=SCORING_WEIGHTS):
        self.resume_parser = EnhancedResumeParser(skill_db)
        self.jd_parser = EnhancedJDParser(skill_db)
        self.scorer = ScoringEngine(weights)
    
    def match(self, resume_text, jd_text):
        """Perform comprehensive resume-JD matching"""
        
        # Parse documents
        resume = self.resume_parser.parse(resume_text)
        jd = self.jd_parser.parse(jd_text)
        
        # Calculate skill matches
        matched_skills = list(set(resume["skills"]) & set(jd["required_skills"]))
        missing_skills = list(set(jd["required_skills"]) - set(resume["skills"]))
        preferred_matched = list(set(resume["skills"]) & set(jd["preferred_skills"]))
        preferred_missing = list(set(jd["preferred_skills"]) - set(resume["skills"]))
        
        # Calculate individual scores
        skill_score = self.scorer.calculate_skill_score(matched_skills, jd["required_skills"])
        exp_score = self.scorer.calculate_experience_score(resume["experience_years"], jd["min_experience"])
        project_score = self.scorer.calculate_project_score(resume["projects"])
        bonus_score = self.scorer.calculate_bonus_score(
            resume["certifications"],
            resume["education"],
            len(preferred_matched)
        )
        
        scores = {
            "skill_match": skill_score,
            "experience_fit": exp_score,
            "project_relevance": project_score,
            "bonus_signals": bonus_score
        }
        
        final, level, msg = self.scorer.final_score(scores)
        
        return {
            "final_score": final,
            "readiness_level": level,
            "summary": msg,
            "strengths": matched_skills,
            "missing_required": missing_skills,
            "preferred_matched": preferred_matched,
            "preferred_missing": preferred_missing,
            "scores": scores,
            "resume_details": {
                "experience_years": resume["experience_years"],
                "project_count": len(resume["projects"]),
                "certification_count": len(resume["certifications"]),
                "education": resume["education"]
            },
            "jd_details": {
                "required_experience": jd["min_experience"],
                "role_level": jd["role_level"]
            }
        }
    
    def generate_heatmap_data(self, report):
        """Generate data for frontend heatmap visualization"""
        skills_data = []
        
        # Matched required skills (green) - type: required, matched: true
        for skill in sorted(report['strengths']):
            skills_data.append({
                'skill': skill.upper(),
                'type': 'required',
                'matched': True,
                'score': 95,
                'status': 'required_matched',
                'color': '#10b981'
            })
        
        # Preferred matched skills (blue) - type: preferred, matched: true
        for skill in sorted(report['preferred_matched'])[:5]:
            skills_data.append({
                'skill': skill.upper(),
                'type': 'preferred',
                'matched': True,
                'score': 75,
                'status': 'preferred_matched',
                'color': '#3b82f6'
            })
        
        # Preferred missing skills (yellow) - type: preferred, matched: false
        for skill in sorted(report['preferred_missing'])[:5]:
            skills_data.append({
                'skill': skill.upper(),
                'type': 'preferred',
                'matched': False,
                'score': 50,
                'status': 'preferred_missing',
                'color': '#f59e0b'
            })
        
        # Missing required skills (red) - type: required, matched: false
        for skill in sorted(report['missing_required'])[:8]:
            skills_data.append({
                'skill': skill.upper(),
                'type': 'required',
                'matched': False,
                'score': 20,
                'status': 'required_missing',
                'color': '#ef4444'
            })
        
        return skills_data


def calculate_ats_score(resume_text, jd_text):
    """
    Main function to calculate ATS score
    
    Args:
        resume_text: Text content of resume
        jd_text: Text content of job description
    
    Returns:
        Dictionary containing score and detailed analysis
    """
    matcher = ATSMatcher()
    report = matcher.match(resume_text, jd_text)
    heatmap_data = matcher.generate_heatmap_data(report)
    
    return {
        'score': report['final_score'],
        'level': report['readiness_level'],
        'summary': report['summary'],
        'report': report,
        'heatmap_data': heatmap_data
    }
