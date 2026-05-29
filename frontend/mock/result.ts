const mockResult = {
  id: 'mock-job-id',
  status: 'completed',
  fileUrl: '/sample-doc.png',
  holder: { name: 'Arjun Mehta', fatherName: 'Rajesh Mehta', dob: '1998-04-12' },
  credential: { degree: 'B.Tech', institution: 'IIT Bombay', year: '2020', cgpa: '9.1' },
  issuer: { name: 'IIT Bombay' },
  confidence: {
    name: 97,
    fatherName: 92,
    dob: 88,
    degree: 95,
    institution: 90,
    year: 85,
    cgpa: 80,
    issuer: 99
  },
  rawText: 'Arjun Mehta\nRajesh Mehta\nB.Tech\nIIT Bombay\n2020\nCGPA: 9.1',
  documentType: 'Degree Certificate',
  createdAt: '2026-05-28T12:00:00Z',
};

export default mockResult;
