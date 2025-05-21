
import { Publication, Researcher } from "../types";

export const currentUser: Researcher = {
  id: "1",
  orcidId: "0000-0001-2345-6789",
  name: "Maria Silva",
  institutionName: "Universidade de São Paulo",
  countryCode: "BR",
  country: "Brazil",
  department: "Department of Computer Science",
  position: "Associate Professor",
  email: "maria.silva@usp.br",
  avatarUrl: "https://randomuser.me/api/portraits/women/44.jpg",
  biography: "Researcher in Natural Language Processing and Machine Learning, with a focus on applications for Portuguese language.",
  website: "https://example.com/mariasilva",
  socialLinks: {
    twitter: "https://twitter.com/mariasilva",
    linkedin: "https://linkedin.com/in/mariasilva",
    googleScholar: "https://scholar.google.com/citations?user=mariasilva",
    researchGate: "https://www.researchgate.net/profile/Maria_Silva",
    github: "https://github.com/mariasilva"
  },
  areaOfExpertise: ["Natural Language Processing", "Machine Learning", "Computational Linguistics"],
  metrics: {
    publications: 45,
    citations: 1250,
    hIndex: 18
  },
  followers: 75,
  following: 52,
  isCompleteProfile: true,
  onboardingStep: 4
};

export const newUser: Researcher = {
  id: "2",
  orcidId: "0000-0002-3456-7890",
  name: "João Santos",
  institutionName: "",
  countryCode: "BR",
  country: "Brazil",
  areaOfExpertise: [],
  metrics: {
    publications: 0,
    citations: 0,
    hIndex: 0
  },
  followers: 0,
  following: 0,
  isCompleteProfile: false,
  onboardingStep: 0
};

export const researchers: Researcher[] = [
  currentUser,
  {
    id: "3",
    orcidId: "0000-0003-4567-8901",
    name: "Carlos Mendes",
    institutionName: "Universidade Estadual de Campinas",
    countryCode: "BR",
    country: "Brazil",
    department: "Institute of Computing",
    position: "Full Professor",
    avatarUrl: "https://randomuser.me/api/portraits/men/42.jpg",
    biography: "Working on distributed systems and cloud computing.",
    areaOfExpertise: ["Distributed Systems", "Cloud Computing", "Software Engineering"],
    metrics: {
      publications: 89,
      citations: 3200,
      hIndex: 25
    },
    followers: 150,
    following: 75,
    isCompleteProfile: true,
    onboardingStep: 4
  },
  {
    id: "4",
    orcidId: "0000-0004-5678-9012",
    name: "Júlia Costa",
    institutionName: "Universidade Federal de Minas Gerais",
    countryCode: "BR",
    country: "Brazil",
    department: "Department of Computer Engineering",
    position: "Assistant Professor",
    avatarUrl: "https://randomuser.me/api/portraits/women/24.jpg",
    areaOfExpertise: ["Computer Vision", "Deep Learning", "Pattern Recognition"],
    metrics: {
      publications: 27,
      citations: 850,
      hIndex: 12
    },
    followers: 45,
    following: 37,
    isCompleteProfile: true,
    onboardingStep: 4
  },
  {
    id: "5",
    orcidId: "0000-0005-6789-0123",
    name: "Alexandre Rodrigues",
    institutionName: "Universidade Federal do Rio de Janeiro",
    countryCode: "BR",
    country: "Brazil",
    department: "Department of Systems Engineering",
    position: "Research Fellow",
    avatarUrl: "https://randomuser.me/api/portraits/men/32.jpg",
    areaOfExpertise: ["Artificial Intelligence", "Robotics", "Human-Computer Interaction"],
    metrics: {
      publications: 36,
      citations: 920,
      hIndex: 14
    },
    followers: 60,
    following: 42,
    isCompleteProfile: true,
    onboardingStep: 4
  },
  {
    id: "6",
    orcidId: "0000-0006-7890-1234",
    name: "Sarah Johnson",
    institutionName: "Stanford University",
    countryCode: "US",
    country: "United States",
    department: "Department of Computer Science",
    position: "Professor",
    avatarUrl: "https://randomuser.me/api/portraits/women/64.jpg",
    areaOfExpertise: ["Machine Learning", "Artificial Intelligence", "Data Mining"],
    metrics: {
      publications: 112,
      citations: 5600,
      hIndex: 32
    },
    followers: 320,
    following: 85,
    isCompleteProfile: true,
    onboardingStep: 4
  },
  {
    id: "7",
    orcidId: "0000-0007-8901-2345",
    name: "Hiroshi Tanaka",
    institutionName: "University of Tokyo",
    countryCode: "JP",
    country: "Japan",
    department: "Department of Information Science",
    position: "Associate Professor",
    avatarUrl: "https://randomuser.me/api/portraits/men/75.jpg",
    areaOfExpertise: ["Data Science", "Big Data Analytics", "Statistical Learning"],
    metrics: {
      publications: 67,
      citations: 2100,
      hIndex: 22
    },
    followers: 130,
    following: 98,
    isCompleteProfile: true,
    onboardingStep: 4
  }
];

export const publications: Publication[] = [
  {
    id: "1",
    title: "Advances in Portuguese Named Entity Recognition using Transformer Models",
    authors: ["Maria Silva", "José Oliveira", "Ana Ferreira"],
    journal: "Computational Linguistics Journal",
    year: 2023,
    doi: "10.1234/clj.2023.1234",
    citations: 8,
    abstract: "This paper presents a novel approach to Named Entity Recognition for the Portuguese language using transformer-based models. We evaluate our approach on multiple datasets and show significant improvements over previous state-of-the-art methods.",
    keywords: ["NLP", "Named Entity Recognition", "Portuguese", "Transformers"],
    link: "https://example.com/paper1",
    type: "journal-article"
  },
  {
    id: "2",
    title: "A Comparative Study of Pre-trained Language Models for Brazilian Portuguese",
    authors: ["Maria Silva", "Carlos Santos", "Luiz Pereira"],
    journal: "Proceedings of PROPOR 2023",
    year: 2023,
    doi: "10.1234/propor.2023.5678",
    citations: 12,
    abstract: "We present a comprehensive comparison of pre-trained language models for Brazilian Portuguese, evaluating their performance on various NLP tasks such as part-of-speech tagging, named entity recognition, and sentiment analysis.",
    keywords: ["Brazilian Portuguese", "Language Models", "NLP", "BERT"],
    link: "https://example.com/paper2",
    type: "conference-paper"
  },
  {
    id: "3",
    title: "BERTimbau: A Large-scale Pre-trained Language Model for Brazilian Portuguese",
    authors: ["Maria Silva", "Paulo Rodrigues", "Teresa Santos", "João Lima"],
    journal: "Journal of Artificial Intelligence Research",
    year: 2022,
    doi: "10.1234/jair.2022.9012",
    citations: 65,
    abstract: "This paper introduces BERTimbau, a pre-trained BERT model for Brazilian Portuguese, trained on a large corpus of Brazilian Portuguese text. We evaluate BERTimbau on a range of NLP tasks and show that it outperforms multilingual models.",
    keywords: ["BERT", "Brazilian Portuguese", "Pre-trained Language Models", "Natural Language Processing"],
    link: "https://example.com/paper3",
    type: "journal-article"
  },
  {
    id: "4",
    title: "Cross-lingual Transfer Learning for Low-resource Portuguese Dialects",
    authors: ["Maria Silva", "António Branco", "Clara Alves"],
    journal: "Transactions of the Association for Computational Linguistics",
    year: 2022,
    doi: "10.1234/tacl.2022.3456",
    citations: 23,
    abstract: "We investigate cross-lingual transfer learning techniques to improve NLP performance on low-resource Portuguese dialects, including those spoken in African countries.",
    keywords: ["Cross-lingual Transfer Learning", "Portuguese", "Low-resource Languages", "NLP"],
    link: "https://example.com/paper4",
    type: "journal-article"
  },
  {
    id: "5",
    title: "PortNER: A Named Entity Recognition Dataset for Portuguese",
    authors: ["Maria Silva", "Ricardo Campos", "Bruno Martins"],
    journal: "Proceedings of LREC 2021",
    year: 2021,
    doi: "10.1234/lrec.2021.7890",
    citations: 34,
    abstract: "We present PortNER, a large manually annotated corpus for Named Entity Recognition in Portuguese, covering both European and Brazilian variants of the language.",
    keywords: ["Named Entity Recognition", "Portuguese", "Corpus", "Dataset"],
    link: "https://example.com/paper5",
    type: "conference-paper"
  },
  {
    id: "6",
    title: "Sentiment Analysis for Portuguese Social Media",
    authors: ["Maria Silva", "Sofia Costa"],
    journal: "Journal of Computational Sociolinguistics",
    year: 2021,
    doi: "10.1234/jcs.2021.1234",
    citations: 19,
    abstract: "This paper presents a sentiment analysis model specifically designed for Portuguese social media text, addressing challenges such as informal language, slang, and code-switching.",
    keywords: ["Sentiment Analysis", "Portuguese", "Social Media", "NLP"],
    link: "https://example.com/paper6",
    type: "journal-article"
  },
  {
    id: "7",
    title: "NLPortuguês: A Toolkit for Natural Language Processing in Portuguese",
    authors: ["Maria Silva", "Guilherme Santos", "Rafaela Mendes"],
    journal: "GitHub Code Repository",
    year: 2020,
    doi: "10.5281/zenodo.1234567",
    citations: 41,
    link: "https://github.com/example/nlportugues",
    type: "code"
  },
];

export const countries = [
  {value: 'BR', label: 'Brazil'},
  {value: 'US', label: 'United States'},
  {value: 'PT', label: 'Portugal'},
  {value: 'JP', label: 'Japan'},
  {value: 'UK', label: 'United Kingdom'},
  {value: 'FR', label: 'France'},
  {value: 'DE', label: 'Germany'},
  {value: 'IT', label: 'Italy'},
  {value: 'ES', label: 'Spain'},
  {value: 'CA', label: 'Canada'},
  {value: 'AU', label: 'Australia'},
];

export const institutions = [
  {value: 'usp', label: 'Universidade de São Paulo'},
  {value: 'unicamp', label: 'Universidade Estadual de Campinas'},
  {value: 'ufmg', label: 'Universidade Federal de Minas Gerais'},
  {value: 'ufrj', label: 'Universidade Federal do Rio de Janeiro'},
  {value: 'stanford', label: 'Stanford University'},
  {value: 'mit', label: 'Massachusetts Institute of Technology'},
  {value: 'oxford', label: 'University of Oxford'},
  {value: 'cambridge', label: 'University of Cambridge'},
  {value: 'tokyo', label: 'University of Tokyo'},
  {value: 'tsinghua', label: 'Tsinghua University'},
];

export const expertiseAreas = [
  "Natural Language Processing",
  "Machine Learning",
  "Artificial Intelligence",
  "Deep Learning",
  "Computer Vision",
  "Data Science",
  "Computational Linguistics",
  "Distributed Systems",
  "Cloud Computing",
  "Big Data Analytics",
  "Human-Computer Interaction",
  "Computer Networks",
  "Software Engineering",
  "Database Systems",
  "Information Retrieval",
  "Cybersecurity",
  "Bioinformatics",
  "Quantum Computing",
  "Robotics",
  "Internet of Things"
];

export const getResearcherById = (id: string): Researcher | undefined => {
  return researchers.find(researcher => researcher.id === id);
};

export const getPublicationsByResearcherId = (id: string): Publication[] => {
  // For demo purposes, we'll just return all publications for the current user
  if (id === "1") {
    return publications;
  }
  return publications.slice(0, 3); // Return first 3 publications for other researchers
};

export const searchResearchers = (query: string): Researcher[] => {
  if (!query) return [];
  const lowerQuery = query.toLowerCase();
  return researchers.filter(
    researcher =>
      researcher.name.toLowerCase().includes(lowerQuery) ||
      researcher.institutionName.toLowerCase().includes(lowerQuery) ||
      researcher.country.toLowerCase().includes(lowerQuery) ||
      researcher.areaOfExpertise.some(area => 
        area.toLowerCase().includes(lowerQuery)
      )
  );
};
