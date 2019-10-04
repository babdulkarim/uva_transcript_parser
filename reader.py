# importing required modules
import PyPDF3
import csv
import sys
import os


# :x should be a course number like 1000 but sometimes it may end with
# a T like 1000T
def is_integer(x):
    try:
        if x[-1:] == "T":
            return True
        int(x)
        return True
    except ValueError:
        return False

# :x should be course credits like 3.00
def is_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def main():
    # creating a pdf file object
    # feed transcript pdf as command line argument
    pdf_input = open(sys.argv[1], 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF3.PdfFileReader(pdf_input)

    # count number of pages in pdf file
    page_count = pdfReader.numPages

    # create list of page objects
    pageObjs = []
    data = []
    for i in range(0, page_count):
        pageObjs.append((pdfReader.getPage(i)))

    # read each page element in the list to extract the text into data list
    for page in pageObjs:
        data.extend(page.extractText().split())

    # we assume student name, date, and footer are constant in every
    # transcript
    student_name = [" ".join(data[:2])]
    date = data[2:3]
    end_footer = [" ".join(data[len(data)-4:])]

    counter = 0
    test_credits = ['Test Credits Applied']
    transfer_credits = ['Transfer Credit from']
    uva_credits = ['Beginning of Undergraduate Record']

    # :TODO check if student has test/transfer credits
    # record test credit like so:
    # course acronym + course number + credits worth
    # record transfer credit like so:
    # translate transferred course acronym + course number + credits worth
    # record UVA credits like so:
    # course acronym + course number + grade received + credits worth

    headers = {'Test Credits Applied': 1, 'Transfer Credit from': 2,
        'Beginning of Undergraduate': 3}

    for i in range(0, len(data)):
        # ignore student name + date
        if i < 3: continue
        # ignore footer
        elif i >= (len(data)-4): continue
        # iterate on transcript data
        else:

            tmp_header = " ".join((data[i], data[i+1], data[i+2]))
            # section = subheader of transcript e.g.
            # test credits/transfer credits/uva credits
            section = headers.get(tmp_header)

            if section is not None:
                counter += section

            # counter == 1 if current section is test credits
            if counter == 1:
                if data[i].isupper() and data[i] != "PT" and data[i] != "TE":
                    # double check that next element is the course number
                    course_num = data[i+1] if is_integer(data[i+1]) else ""
                    credits_num = data[i+4] if is_float(data[i+4]) else ""
                    course = " ".join((data[i], course_num))

                    if len(course) > 4:
                        test_credits.append(course)

                if " ".join((data[i], data[i+1],
                data[i+2])) == "Test Credit Total:":
                    total_credits = " ".join((data[i], data[i+1],
                                        data[i+2], data[i+3]))
                    test_credits.append(total_credits)

            # counter == 3 if current section is transfer credits
            if counter == 3:
                if data[i].isupper() and data[i] != "PT" and data[i] != "TE":
                    if data[i-1] == "as":
                        # double check that next element is the course number
                        course_num = data[i+1] if is_integer(data[i+1]) else ""
                        credits_num = data[i+4] if is_float(data[i+4]) else ""
                        course = " ".join((data[i], course_num))

                        if len(course) > 4:
                            transfer_credits.append(course)

                if " ".join((data[i], data[i+1],
                data[i+2])) == "Transfer Credit Total:":
                    total_credits = " ".join((data[i], data[i+1],
                                        data[i+2], data[i+3]))
                    transfer_credits.append(total_credits)

            # counter == 6 if current section is uva credits
            if counter == 6:
                if data[i].isupper() and data[i] != "PT" and data[i] != "TE":
                    # double check that next element is the course number
                    course_num = data[i+1] if is_integer(data[i+1]) else ""
                    grade = ""
                    credits_num = data[i+4] if is_float(data[i+4]) else ""
                    course = " ".join((data[i], course_num))

                    if len(course) > 4:
                        uva_credits.append(course)

    # write all data to csv file
    with open('transcript.csv', mode='w') as transcript_file:
        transcript_writer = csv.writer(transcript_file, delimiter='\n',
                                lineterminator=os.linesep, quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)

        transcript_writer.writerow(student_name)
        transcript_writer.writerow(date)

        # only write to csv if student has test credits
        if len(test_credits) > 1:
            transcript_writer.writerow(test_credits)

        # only write to csv if student has transfer credits
        if len(transfer_credits) > 1:
            transcript_writer.writerow(transfer_credits)

        # only write to csv if student has uva credits
        if len(uva_credits) > 1:
            transcript_writer.writerow(uva_credits)

        transcript_writer.writerow(end_footer)

    # closing the pdf file object
    pdf_input.close()


if __name__=="__main__":
    main()
