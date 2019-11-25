def str2list(data):
  length = len(data)
  data = data[1:length-1]
  data = data.split(',')
  return data