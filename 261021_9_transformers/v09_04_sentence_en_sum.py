from transformers import pipeline

# 1. 요약 파이프라인
summerizer = pipeline("summarization", model="t5-small")

# 2. 요약할 문장
text = """
MEMORANDUM OF PROCEDURAL CLARIFICATION REGARDING THE ADMINISTRATION OF SUPPLEMENTARY FACILITY USAGE PROVISIONS

Section 1: Preliminary Considerations and General Observations

Whereas it has been previously determined, pursuant to the deliberations of the Committee on Operational Continuity (hereinafter referred to as “the Committee”), that the existing framework governing the utilization of shared facilities, including but not limited to meeting rooms, storage areas, and common recreational spaces (hereinafter collectively referred to as “the Facilities”), requires certain clarifications, amendments, and supplementary provisions, the undersigned hereby sets forth the following considerations, which shall be read in conjunction with, and not in derogation of, any and all prior memoranda, notices, circulars, and informal communications that may have been issued on the subject, whether or not such documents are expressly referenced herein.

It is to be understood that nothing contained in this Memorandum shall be construed as altering, diminishing, or otherwise affecting the rights and obligations of any party, except insofar as such rights and obligations are expressly altered, diminished, or affected by the provisions set forth hereinafter, and subject always to the exceptions, qualifications, and limitations enumerated in Section 7, which shall apply mutatis mutandis to all matters not otherwise addressed.

Section 2: Definitions and Interpretive Principles

For the purposes of this Memorandum, the term “User” shall mean any individual, group, department, or affiliated entity that, at any time during the relevant period, has requested, reserved, accessed, or otherwise made use of any of the Facilities, regardless of whether such use was authorized, scheduled, or recorded in the official register. The term “Relevant Period” shall mean the period commencing on the date of the first reservation and continuing until such time as the last reservation has been duly concluded, closed, and archived.

The term “Reasonable Notice” shall be interpreted in a manner consistent with the customary practices of the organization, taking into account the nature of the request, the availability of staff, the season, and any other factor that the administrator, in their sole discretion, may deem relevant. Where the meaning of any term remains unclear after the application of the foregoing principles, the interpretation preferred by the Committee shall prevail.

Section 3: Reservation Procedures

All reservations of the Facilities shall be submitted through the designated online portal, which has been made available for this purpose and which shall be considered the primary, though not exclusive, channel for the submission of requests. Users are reminded that the portal is subject to periodic maintenance, during which it may be temporarily unavailable, and that such unavailability shall not, in and of itself, constitute grounds for the waiver of any deadline.

Effective from the first day of January of the coming year, a reservation fee of twelve thousand won per hour shall be applied to all reservations of the large meeting room, it being understood that this fee replaces the previously applicable flat rate and shall be invoiced on a monthly basis. Reservations of the small meeting rooms and the storage areas shall remain free of charge, subject to the conditions described elsewhere in this Memorandum.

Requests must be submitted no later than five business days before the intended date of use. Requests submitted after this deadline may be considered at the discretion of the administrator but shall not be guaranteed, and the administrator shall bear no obligation to provide reasons for any refusal.

Section 4: Cancellation and Modification

A User wishing to cancel or modify a reservation shall notify the administrator in writing, by means of the portal or by electronic mail, at least forty-eight hours before the commencement of the reserved period. Cancellations made within the said forty-eight-hour period shall be subject to a penalty equal to fifty percent of the applicable fee, except where the cancellation is attributable to circumstances beyond the reasonable control of the User, as determined by the administrator after consideration of any supporting documentation that the User may be requested to provide.

It is further noted that repeated cancellations, whether or not accompanied by supporting documentation, may be taken into account in the evaluation of future requests, in a manner to be determined from time to time.

Section 5: Conduct and Responsibilities of Users

Users shall, at all times, conduct themselves in a manner that is respectful of other Users, of the staff, and of the Facilities themselves. Food and beverages may be consumed in the common recreational spaces only; consumption in the meeting rooms is prohibited, with the sole exception of water in closed containers. Users shall be responsible for restoring the Facilities to the condition in which they were found, and any damage, loss, or excessive soiling shall be reported to the administrator without delay.

Where a User fails to comply with the foregoing obligations, the administrator may, following a written warning, suspend that User’s access for a period not exceeding thirty days, without prejudice to any other remedy available under applicable regulations.

Section 6: Records, Data, and Review

All reservation records shall be retained for a period of three years from the date of the last entry, after which they shall be disposed of in accordance with the organization’s data retention policy. The Committee shall review the operation of these provisions on an annual basis and may recommend amendments as it sees fit, which shall take effect upon publication.

Section 7: Exceptions, Qualifications, and Final Provisions

Notwithstanding anything to the contrary contained in the preceding Sections, the Committee reserves the right to waive, suspend, or modify any provision of this Memorandum in respect of any User, Facility, or period, where it considers such action to be in the interest of the organization. Emergency use of the Facilities by the safety team shall not be subject to the reservation procedures or fees described herein. Any inquiries regarding this Memorandum should be directed to the Office of Facilities Administration, which will respond within a reasonable time, as defined in Section 2.

This Memorandum shall be deemed to have been duly communicated upon its publication on the internal notice board, irrespective of whether any particular User has actually read it.
"""

# 3. 요약 실행
summary = summerizer(
    text,
    min_length=20,  # 최소 토큰
    max_length=100,  # 최대 토큰
    do_sample=False,  # 매번 동일 결과 출력
)

# 4. 결과 확인
sum_text = summary[0]["summary_text"]
print(f"요약된 결과 : {sum_text}")